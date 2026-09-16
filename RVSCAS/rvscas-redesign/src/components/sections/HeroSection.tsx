import { motion } from "framer-motion"
import { ArrowRight, Play } from "lucide-react"
import { Button } from "@/components/ui/button"

export default function HeroSection() {
  return (
    <section id="home" className="relative min-h-screen flex items-center overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-b from-[#0a0f1e]/60 via-transparent to-[#0a0f1e]/80 z-0" />

      <div className="relative z-10 mx-auto max-w-6xl px-4 pt-24 w-full">
        <div className="flex flex-col items-center text-center">
          <motion.span
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="inline-flex items-center gap-2 rounded-full border border-accent/30 bg-accent/10 px-4 py-1.5 text-sm text-accent mb-6"
          >
            <span className="w-2 h-2 rounded-full bg-accent animate-pulse" />
            NAAC A+ Accredited | Autonomous | Since 1986
          </motion.span>

          <motion.h1
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.2 }}
            className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold text-white leading-tight"
          >
            Choose Excellence at{" "}
            <span className="text-gradient">RVS CAS</span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.3 }}
            className="mt-6 text-lg text-white/60 max-w-3xl"
          >
            Approved by the National Institutional Ranking Framework (NIRF).
            Elevate your education with top-notch accreditation.
            Affordable and Quality Education for all —{" "}
            <span className="text-accent font-semibold">is our vision.</span>
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.5 }}
            className="mt-10 flex flex-col sm:flex-row gap-4"
          >
            <a href="https://admissions.rvscas.ac.in/" target="_blank" rel="noopener noreferrer" onClick={(e) => e.stopPropagation()}>
              <Button variant="glow" size="lg" className="group">
                Explore Programs
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Button>
            </a>
            <a href="https://youtu.be/6Z3jYxlyvww" target="_blank" rel="noopener noreferrer" onClick={(e) => e.stopPropagation()}>
              <Button variant="outline" size="lg" className="group">
                <Play className="w-5 h-5" />
                Virtual Tour
              </Button>
            </a>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.7 }}
            className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-4 w-full max-w-4xl"
          >
            {[
              { label: "NAAC Grade", value: "A+" },
              { label: "UG / PG Programs", value: "38+" },
              { label: "Placement Rate", value: "92%" },
              { label: "Years of Excellence", value: "39+" },
            ].map((stat, i) => (
              <div
                key={i}
                className="glass rounded-xl px-4 py-5 text-center hover:bg-white/5 transition-all"
              >
                <div className="text-2xl md:text-3xl font-bold text-accent">{stat.value}</div>
                <div className="text-xs text-white/50 mt-1 uppercase tracking-wider">{stat.label}</div>
              </div>
            ))}
          </motion.div>

          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1, delay: 1 }}
            className="mt-10 text-white/40 text-sm"
          >
            Rathnavel Subramaniam (RVS) College of Arts and Science (Autonomous)
          </motion.p>
        </div>
      </div>
    </section>
  )
}
