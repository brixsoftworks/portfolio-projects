import { createClient } from "https://esm.sh/@supabase/supabase-js@2.45.4";
import { evaluateTask, type EventRow, type RuleRow } from "./_shared/evaluator.ts";

const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SUPABASE_ANON_KEY = Deno.env.get("SUPABASE_ANON_KEY")!;
const SERVICE_ROLE_KEY = Deno.env.get("SERVICE_ROLE_KEY") ?? "";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers":
    "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};

interface Payload {
  taskId: string;
}

/**
 * verify-task
 *
 * Server-authoritative verification of a single task:
 *   1. Authenticates the caller.
 *   2. Loads the task (ownership is enforced by RLS).
 *   3. Loads the task's rules and the normalized evidence events uploaded
 *      by the device during the task window.
 *   4. Evaluates every rule on the server (see _shared/evaluator.ts).
 *   5. Persists the verdict in verification_state and appends audit rows.
 *
 * The device can trigger this when the user asks to verify; the verdict it
 * receives is produced here, not locally.
 */
Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }
  if (req.method !== "POST") {
    return new Response(JSON.stringify({ error: "method not allowed" }), {
      status: 405,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }

  const authHeader = req.headers.get("Authorization") ?? "";
  const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
    global: { headers: { Authorization: authHeader } },
  });

  const { data: userData, error: authError } = await supabase.auth.getUser(
    authHeader.replace("Bearer ", ""),
  );
  if (authError || !userData.user) {
    return new Response(JSON.stringify({ error: "unauthorized" }), {
      status: 401,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }
  const userId = userData.user.id;

  let body: Payload;
  try {
    body = await req.json() as Payload;
  } catch {
    return new Response(JSON.stringify({ error: "invalid body" }), {
      status: 400,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }
  if (!body.taskId) {
    return new Response(JSON.stringify({ error: "taskId required" }), {
      status: 400,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }

  // RLS scopes the task lookup to this user, so a foreign task simply
  // returns nothing - no information leak about which ids exist.
  const { data: taskRows } = await supabase
    .from("tasks")
    .select("id, starts_at, ends_at, status")
    .eq("id", body.taskId)
    .limit(1);

  const task = taskRows?.[0];
  if (!task) {
    return new Response(JSON.stringify({ error: "task not found" }), {
      status: 404,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }

  const { data: ruleRows } = await supabase
    .from("verification_rules")
    .select("*")
    .eq("task_id", task.id) as { data: RuleRow[] | null };

  const { data: eventRows } = await supabase
    .from("verification_events")
    .select("*")
    .eq("task_id", task.id)
    .gte("occurred_at", new Date(task.starts_at / 1_000).toISOString())
    .lte("occurred_at", new Date(task.ends_at / 1_000).toISOString())
    .order("occurred_at", { ascending: true }) as { data: EventRow[] | null };

  const rules = ruleRows ?? [];
  const events = eventRows ?? [];
  const { perRule, verified } = evaluateTask(rules, events);

  // Persist the verdict. Use the service role for the upsert + audit write so
  // the writes are atomic with the decision taken here.
  const admin = createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
    global: { headers: { Authorization: `Bearer ${SERVICE_ROLE_KEY}` } },
  });
  if (SERVICE_ROLE_KEY) {
    await admin
      .from("verification_state")
      .upsert({
        task_id: task.id,
        provider: rules[0]?.provider ?? "none",
        is_verified: verified,
        last_checked_at: new Date().toISOString(),
        events_json: events,
      });
    await admin.from("audit_events").insert({
      user_id: userId,
      device_id: "server",
      task_id: task.id,
      type: verified ? "verification_passed" : "verification_failed",
      payload: { perRule, checkedAt: new Date().toISOString() },
    });
  }

  return new Response(
    JSON.stringify({
      taskId: task.id,
      verified,
      rules: perRule,
      deviceStatus: task.status,
    }),
    {
      status: 200,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    },
  );
});