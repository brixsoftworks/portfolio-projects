import { useRef } from "react"
import { motion, useInView } from "framer-motion"
import { Briefcase, TrendingUp, Building, Award, ExternalLink } from "lucide-react"

const placementStats = [
  { value: "₹6.1 LPA", label: "Highest Package", icon: TrendingUp },
  { value: "₹4.3 LPA", label: "Average Package", icon: Award },
  { value: "92%", label: "Placement Rate", icon: Briefcase },
  { value: "97+", label: "Recruiting Companies", icon: Building },
]

const topRecruiters = [
  "TCS", "Infosys", "Cognizant", "Deloitte", "Wipro",
  "Godrej", "LTI Mindtree", "Larsen & Toubro", "Muthoot Finance",
  "ABT Maruti", "Joy Alukkas", "Amazon",
]

export default function PlacementAcademy() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true })

  return (
    <section id="placements" className="relative py-20 overflow-hidden">
      <div className="absolute inset-0 bg-[#0a0f1e]/40 backdrop-blur-[2px]" />
      <div className="absolute top-0 right-0 w-[400px] h-[400px] bg-secondary/5 rounded-full blur-[100px]" />

      <div ref={ref} className="relative z-10 mx-auto max-w-7xl px-4">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <h2 className="text-2xl md:text-4xl font-bold text-white">
            Placement Training <span className="text-gradient">Academy</span>
          </h2>
          <p className="mt-3 text-white/50">
            Dedicated placement cell ensuring every student launches their dream career
          </p>
        </motion.div>

        <div className="grid md:grid-cols-2 gap-8 mb-10">
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            animate={isInView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <div className="glass rounded-2xl p-6 md:p-8">
              <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-accent" />
                Placement Highlights 2025
              </h3>
              <div className="grid grid-cols-2 gap-4">
                {placementStats.map((stat, i) => (
                  <div key={i} className="bg-white/5 rounded-xl p-4 text-center">
                    <stat.icon className="w-6 h-6 text-accent mx-auto mb-2" />
                    <div className="text-xl md:text-2xl font-bold text-white">{stat.value}</div>
                    <div className="text-xs text-white/50 mt-0.5">{stat.label}</div>
                  </div>
                ))}
              </div>
              <p className="text-white/40 text-sm mt-6 leading-relaxed">
                Contact Person: Mr. MA. Rajesh Kumar &mdash; 9578035000
                <br />
                Email: placementrvscas@rvsgroup.com
              </p>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 30 }}
            animate={isInView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.3 }}
          >
            <div className="glass rounded-2xl p-6 md:p-8">
              <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                <Building className="w-5 h-5 text-accent" />
                Top Recruiters
              </h3>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                {topRecruiters.map((name, i) => (
                  <div
                    key={i}
                    className="bg-white/5 rounded-lg px-3 py-3 text-center text-white/70 text-sm font-medium hover:bg-accent/10 hover:text-accent transition-all"
                  >
                    {name}
                  </div>
                ))}
              </div>
              <div className="mt-6 flex items-center gap-4 text-sm">
                <a href="https://rvscas.ac.in/placement/records" target="_blank" rel="noopener noreferrer" className="flex items-center gap-1 text-accent hover:underline">
                  View Placement Report <ExternalLink className="w-3 h-3" />
                </a>
                <a href="https://rvscas.ac.in/placement/gallery" target="_blank" rel="noopener noreferrer" className="flex items-center gap-1 text-accent hover:underline">
                  Placement Gallery <ExternalLink className="w-3 h-3" />
                </a>
              </div>
            </div>
          </motion.div>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="glass rounded-2xl p-6 md:p-8 text-center"
        >
          <h3 className="text-xl font-bold text-white mb-2">Teaching Learning Process</h3>
          <p className="text-white/50 max-w-3xl mx-auto">
            Activity based training with industry-relevant curriculum designed to meet
            the demands of the current and future industry landscape.
          </p>
          <div className="flex flex-wrap justify-center gap-3 mt-5">
            {["Industry-Relevant Curriculum", "Expert Faculty", "Hands-on Training", "Skill Development"].map((item, i) => (
              <span key={i} className="inline-flex items-center gap-1.5 rounded-full bg-accent/10 border border-accent/20 px-4 py-1.5 text-sm text-accent">
                <span className="w-1.5 h-1.5 rounded-full bg-accent" />
                {item}
              </span>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  )
}
