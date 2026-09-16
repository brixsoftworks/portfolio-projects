import { useRef } from "react"
import { motion, useInView } from "framer-motion"
import { FileText, ExternalLink, ScrollText, Newspaper, Users, ShieldCheck } from "lucide-react"

const links = [
  { icon: FileText, title: "NIRF", desc: "National Institutional Ranking Framework", link: "https://rvscas.ac.in/nirf" },
  { icon: ScrollText, title: "NAAC SSR Report - Cycle 4", desc: "Self Study Report for accreditation", link: "https://rvscas.ac.in/pdf/Naac%20page%20pdf/NACC-Cycle/SSR-Fourth%20Cycle_compressed.pdf" },
  { icon: FileText, title: "IQAC Reports", desc: "Internal Quality Assurance Cell reports", link: "https://rvscas.ac.in/iqac" },
  { icon: Newspaper, title: "Press Coverage", desc: "Media coverage and news articles", link: "https://rvscas.ac.in/campus/press-coverage" },
  { icon: Users, title: "Alumni", desc: "Connect with our alumni network", link: "https://rvscas.ac.in/campus/alumini-staff" },
  { icon: ShieldCheck, title: "Certificate Verification", desc: "Verify your documents online", link: "https://rvscas.directverify.in/student/#/app/request" },
]

export default function QuickLinks() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true })

  return (
    <section id="quick-links" className="relative py-20 overflow-hidden">
      <div className="absolute inset-0 bg-[#0a0f1e]/40 backdrop-blur-[2px]" />
      <div className="absolute top-0 left-1/3 w-[400px] h-[400px] bg-accent/5 rounded-full blur-[100px]" />

      <div ref={ref} className="relative z-10 mx-auto max-w-7xl px-4">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <h2 className="text-2xl md:text-4xl font-bold text-white">
            Quick <span className="text-gradient">Links</span>
          </h2>
          <p className="mt-3 text-white/50">Important resources at your fingertips</p>
        </motion.div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {links.map((link, i) => (
            <motion.a
              key={i}
              href={link.link}
              target="_blank"
              rel="noopener noreferrer"
              initial={{ opacity: 0, y: 30 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.5, delay: i * 0.08 }}
              className="glass rounded-xl p-5 flex items-start gap-4 hover:bg-white/5 transition-all group"
            >
              <div className="w-12 h-12 rounded-xl bg-accent/10 flex items-center justify-center shrink-0 group-hover:scale-110 transition-transform">
                <link.icon className="w-6 h-6 text-accent" />
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="text-white font-semibold group-hover:text-accent transition-colors">
                  {link.title}
                </h3>
                <p className="text-white/40 text-sm mt-0.5">{link.desc}</p>
              </div>
              <ExternalLink className="w-4 h-4 text-white/30 shrink-0 mt-1 group-hover:text-accent transition-colors" />
            </motion.a>
          ))}
        </div>
      </div>
    </section>
  )
}
