import { getFestivals, MONTH_NAMES } from "@/data/catalog";
import { FestivalCard } from "@/components/FestivalCard";

export default async function FestivalsPage() {
  const festivals = await getFestivals();
  const grouped = festivals.reduce<Record<number, typeof festivals>>((acc, f) => {
    (acc[f.month] ??= []).push(f);
    return acc;
  }, {});

  return (
    <main className="mx-auto max-w-7xl flex-grow px-4 py-10 sm:px-6 lg:px-8">
      <div className="mb-10">
        <p className="eyebrow-soft mb-4">Calendar</p>
        <h1 className="text-4xl font-bold tracking-tight text-ink lg:text-5xl">
          Festival Calendar of India
        </h1>
        <p className="mt-4 max-w-2xl text-ink-muted">
          A country that celebrates in every month of the year. Browse the
          pan-India celebrations observed across every state and union
          territory.
        </p>
      </div>

      <div className="space-y-12">
        {Array.from({ length: 12 }, (_, i) => i + 1)
          .filter((m) => grouped[m])
          .map((m) => (
            <section key={m}>
              <div className="mb-5 flex items-baseline gap-3">
                <h2 className="text-2xl font-bold text-ink">
                  {MONTH_NAMES[m - 1]}
                </h2>
                <span className="chip">{grouped[m].length} festivals</span>
              </div>
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
                {grouped[m].map((f) => (
                  <FestivalCard key={f.slug} festival={f} />
                ))}
              </div>
            </section>
          ))}
      </div>
    </main>
  );
}
