import { useRef } from "react"
import { motion, useInView } from "framer-motion"
import { ExternalLink, Sparkles, Monitor, Heart, Award, BookOpen } from "lucide-react"

const highlights = [
  {
    icon: Award,
    title: "NAAC A+ Accredited",
    desc: "Re-accredited with A+ grade by NAAC, reflecting our commitment to quality education.",
  },
  {
    icon: Monitor,
    title: "School of Computer Studies",
    desc: "BCA, B.Sc CS, MCA, M.Sc CS & IT — industry-aligned computer programs.",
    link: "https://rvscas.ac.in/academics/school-of-computer/",
  },
  {
    icon: Sparkles,
    title: "RVS Yuva",
    desc: "Student-centric initiative for holistic development and talent showcase.",
    link: "http://rvsyuva.org/",
  },
  {
    icon: Heart,
    title: "Anti-Sexual Harassment Cell",
    desc: "Safe and respectful campus environment for all.",
  },
  {
    icon: BookOpen,
    title: "Unnat Bharat Abhiyan",
    desc: "Connecting higher education institutions with local communities.",
  },
]

export default function Highlights() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true })

  return (
    <section id="highlights" className="relative py-20 overflow-hidden">
      <div className="absolute inset-0 bg-[#0a0f1e]/40 backdrop-blur-[2px]" />
      <div className="absolute bottom-0 right-1/3 w-[500px] h-[500px] bg-secondary/5 rounded-full blur-[120px]" />

      <div ref={ref} className="relative z-10 mx-auto max-w-7xl px-4">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <h2 className="text-2xl md:text-4xl font-bold text-white">
            <span className="text-gradient">Highlights</span>
          </h2>
          <p className="mt-3 text-white/50">What makes RVS CAS stand out</p>
        </motion.div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {highlights.map((item, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 30 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.5, delay: i * 0.08 }}
              className="glass rounded-2xl p-6 hover:bg-white/5 transition-all group"
            >
              <div className="w-12 h-12 rounded-xl bg-accent/10 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <item.icon className="w-6 h-6 text-accent" />
              </div>
              <h3 className="text-lg font-bold text-white mb-2">{item.title}</h3>
              <p className="text-white/50 text-sm leading-relaxed">{item.desc}</p>
              {item.link && (
                <a
                  href={item.link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 text-accent text-sm mt-3 hover:underline"
                >
                  Learn More <ExternalLink className="w-3 h-3" />
                </a>
              )}
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
