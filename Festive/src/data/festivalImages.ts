// Festival images downloaded from Wikimedia Commons (CC/Public domain).
// Keyed by festival slug; festivals without an image fall back to the state-outline art.
// See /tmp/opencode/festival_images_manifest.json for source + license attribution.
export const FESTIVAL_IMAGES: Record<string, string> = {
  "baisakhi": "/images/festivals/baisakhi.jpg?v=2",
  "buddha-purnima": "/images/festivals/buddha-purnima.jpg?v=2",
  "christmas": "/images/festivals/christmas.jpg?v=2",
  "diwali": "/images/festivals/diwali.jpg?v=2",
  "durga-puja": "/images/festivals/durga-puja.jpg?v=2",
  "dussehra-vijayadashami": "/images/festivals/dussehra-vijayadashami.jpg?v=2",
  "eid-ul-adha-bakrid": "/images/festivals/eid-ul-adha-bakrid.jpg?v=2",
  "eid-ul-fitr": "/images/festivals/eid-ul-fitr.jpg?v=2",
  "gandhi-jayanti": "/images/festivals/gandhi-jayanti.jpg?v=2",
  "ganesh-chaturthi": "/images/festivals/ganesh-chaturthi.jpg?v=2",
  "guru-nanak-jayanti": "/images/festivals/guru-nanak-jayanti.jpg?v=2",
  "holi": "/images/festivals/holi.jpg?v=2",
  "independence-day": "/images/festivals/independence-day.jpg?v=2",
  "janmashtami": "/images/festivals/janmashtami.jpg?v=2",
  "karva-chauth": "/images/festivals/karva-chauth.jpg?v=2",
  "kumbh-mela": "/images/festivals/kumbh-mela.jpg?v=2",
  "lohri": "/images/festivals/lohri.jpg?v=2",
  "maha-shivratri": "/images/festivals/maha-shivratri.jpg?v=2",
  "makar-sankranti": "/images/festivals/makar-sankranti.jpg?v=2",
  "navratri": "/images/festivals/navratri.jpg?v=2",
  "onam": "/images/festivals/onam.jpg?v=2",
  "pongal": "/images/festivals/pongal.jpg?v=2",
  "rakhi-nariyal-poornima": "/images/festivals/rakhi-nariyal-poornima.jpg?v=2",
  "raksha-bandhan": "/images/festivals/raksha-bandhan.jpg?v=2",
  "rath-yatra": "/images/festivals/rath-yatra.jpg?v=2",
  "republic-day": "/images/festivals/republic-day.jpg?v=2",
  "ugadi-gudi-padwa": "/images/festivals/ugadi-gudi-padwa.jpg?v=2",
  "vishu": "/images/festivals/vishu.jpg?v=2",
};

export function festivalImage(slug: string): string | undefined {
  return FESTIVAL_IMAGES[slug];
}
