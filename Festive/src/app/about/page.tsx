
import { Icon } from "@/components/icons";

const PROMISES = [
  {
    icon: "check_circle" as const,
    title: "Curated artisan products",
    body: "Authentic items sourced directly from local artisans across India.",
  },
  {
    icon: "calendar_month" as const,
    title: "Festival calendar for each state",
    body: "Never miss a celebration with our detailed regional guides.",
  },
  {
    icon: "local_shipping" as const,
    title: "Fair prices & fast delivery",
    body: "Transparent pricing and reliable nationwide shipping.",
  },
  {
    icon: "security" as const,
    title: "Razorpay-secured payments",
    body: "100% safe and secure transactions for peace of mind.",
  },
];

export default async function AboutPage() {
  return (
    <main className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
      <section className="mb-16 w-full rounded-3xl bg-slate-950 p-12 text-center text-white shadow-xl relative overflow-hidden">
        <h1 className="mb-6 text-5xl font-bold tracking-tight md:text-6xl">
          About The Divine Things
        </h1>
        <p className="mx-auto max-w-3xl text-lg text-white/80 md:text-xl">
          One store for every festival of India — because no two celebrations are
          alike, and neither should your shopping be.
        </p>
      </section>



      <section className="mx-auto mb-20 max-w-3xl rounded-3xl border border-black/5 bg-white p-8 shadow-sm md:p-12">
        <div className="mb-12">
          <h2 className="mb-6 text-center text-3xl font-bold tracking-tight text-ink md:text-4xl">
            Why The Divine Things exists
          </h2>
          <p className="mb-4 leading-relaxed text-ink-muted">
            India is a land of vivid colors, diverse cultures, and endless
            celebrations. From the vibrant Navratri of Gujarat to the grand Durga
            Puja of Bengal, from the illuminating Diwali of the North to the
            harvest joys of Pongal in the South, every state has its unique spirit.
          </p>
          <p className="leading-relaxed text-ink-muted">
            We noticed that finding authentic items for specific regional festivals
            was often a challenge if you lived outside your home state. The Divine Things was
            born from a simple idea: to make the unique traditions of all 28 states
            and 8 union territories accessible to every Indian, no matter where
            they live. We bring the celebration to your doorstep.
          </p>
        </div>
        <div>
          <h2 className="mb-6 text-center text-3xl font-bold tracking-tight text-ink md:text-4xl">
            Our promise
          </h2>
          <ul className="space-y-4">
            {PROMISES.map((item) => (
              <li key={item.title} className="flex items-start gap-4">
                <Icon name={item.icon} className="mt-1 h-6 w-6 shrink-0 text-success" />
                <div>
                  <strong className="block text-ink">{item.title}</strong>
                  <span className="text-sm text-ink-muted">{item.body}</span>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </section>
    </main>
  );
}
