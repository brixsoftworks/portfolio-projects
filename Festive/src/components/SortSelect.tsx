"use client";

import { useRouter, usePathname } from "next/navigation";
import { useCallback } from "react";
import { Icon } from "@/components/icons";

export const SORT_OPTIONS = [
  { key: "featured", label: "Relevance" },
  { key: "price-asc", label: "Price: Low to High" },
  { key: "price-desc", label: "Price: High to Low" },
  { key: "rating", label: "Customer Rating" },
] as const;

export function SortSelect({ current }: { current: string }) {
  const router = useRouter();
  const pathname = usePathname();

  const onChange = useCallback(
    (e: React.ChangeEvent<HTMLSelectElement>) => {
      const params = new URLSearchParams(window.location.search);
      params.set("sort", e.target.value);
      router.push(`${pathname}?${params.toString()}`);
    },
    [pathname, router]
  );

  return (
    <div className="relative">
      <select
        value={current}
        onChange={onChange}
        className="block w-full cursor-pointer appearance-none rounded-lg border border-stone-300 bg-white py-2 pl-3 pr-10 text-sm text-ink focus:border-primary focus:outline-none focus:ring-primary"
      >
        {SORT_OPTIONS.map((s) => (
          <option key={s.key} value={s.key}>
            {s.label}
          </option>
        ))}
      </select>
      <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-stone-500">
        <Icon name="expand_more" className="h-5 w-5" />
      </div>
    </div>
  );
}
