import { useRef } from "react"
import { motion, useInView } from "framer-motion"
import { Building, ScrollText, Handshake, Monitor, Shield, BookOpen, FileText } from "lucide-react"

const infoItems = [
  { icon: Building, title: "College", desc: "RVS College of Arts and Science (Autonomous)", link: "https://rvscas.ac.in/about" },
  { icon: ScrollText, title: "Research Policy", desc: "Promoting research and innovation", link: "https://rvscas.ac.in/research" },
  { icon: Handshake, title: "MoU's", desc: "Strategic partnerships with industries", link: "https://rvscas.ac.in/research" },
  { icon: Monitor, title: "IT Policy", desc: "Information Technology guidelines", link: "#" },
  { icon: Shield, title: "RTI", desc: "Right to Information Act", link: "https://rvscas.ac.in" },
  { icon: BookOpen, title: "AISHE", desc: "All India Survey on Higher Education", link: "https://rvscas.ac.in" },
  { icon: FileText, title: "NISP Policy", desc: "National Innovation and Startup Policy", link: "https://rvscas.ac.in" },
]

export default function InfoSection() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true })

  return (
    <section id="info" className="relative py-20 overflow-hidden">
      <div className="absolute inset-0 bg-[#0a0f1e]/40 backdrop-blur-[2px]" />
      <div className="absolute top-0 right-0 w-[400px] h-[400px] bg-primary-light/10 rounded-full blur-[100px]" />

      <div ref={ref} className="relative z-10 mx-auto max-w-7xl px-4">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <h2 className="text-2xl md:text-4xl font-bold text-white">
            <span className="text-gradient">Information</span>
          </h2>
          <p className="mt-3 text-white/50">Important policies and resources</p>
        </motion.div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {infoItems.map((item, i) => (
            <motion.a
              key={i}
              href={item.link || "#"}
              target={item.link && item.link !== "#" ? "_blank" : undefined}
              rel={item.link && item.link !== "#" ? "noopener noreferrer" : undefined}
              initial={{ opacity: 0, y: 20 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.4, delay: i * 0.06 }}
              className="glass rounded-xl p-4 flex items-center gap-4 hover:bg-white/5 transition-all group cursor-pointer"
            >
              <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center shrink-0 group-hover:scale-110 transition-transform">
                <item.icon className="w-5 h-5 text-accent" />
              </div>
              <div>
                <h3 className="text-white font-semibold text-sm">{item.title}</h3>
                <p className="text-white/40 text-xs mt-0.5">{item.desc}</p>
              </div>
            </motion.a>
          ))}
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, delay: 0.5 }}
          className="mt-12 glass rounded-2xl p-6 md:p-8"
        >
          <h3 className="text-lg font-bold text-white mb-4 text-center">
            Faculty Excellence Award 2024
          </h3>
          <div className="flex flex-wrap justify-center gap-4 text-sm text-white/50">
            <a href="https://nptel.ac.in/" target="_blank" rel="noopener noreferrer" className="glass rounded-lg px-4 py-2">NPTEL</a>
            <a href="https://swayam.gov.in/" target="_blank" rel="noopener noreferrer" className="glass rounded-lg px-4 py-2">Swayam</a>
            <a href="https://vidyamitra.inflibnet.ac.in/" target="_blank" rel="noopener noreferrer" className="glass rounded-lg px-4 py-2">Vidya-Mitra</a>
            <a href="http://epgp.inflibnet.ac.in/" target="_blank" rel="noopener noreferrer" className="glass rounded-lg px-4 py-2">Gateway to All PG Courses</a>
            <a href="https://sakshat.ac.in/" target="_blank" rel="noopener noreferrer" className="glass rounded-lg px-4 py-2">Sakshat</a>
            <a href="https://www.youth4work.com/onlinetalenttest/" target="_blank" rel="noopener noreferrer" className="glass rounded-lg px-4 py-2">Skill Test For Students</a>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
