import { useRef } from "react"
import { motion, useInView } from "framer-motion"
import { Lightbulb, Image, BookOpen, ExternalLink } from "lucide-react"

const items = [
  {
    icon: Lightbulb,
    title: "RVS Quiz Club",
    desc: "Test your knowledge and win exciting prizes",
    link: "https://rvscas.ac.in/campus/quiz",
  },
  {
    icon: Image,
    title: "Photo Gallery",
    desc: "Browse campus events and memories",
    link: "https://rvscas.ac.in/placement/gallery",
  },
  {
    icon: Lightbulb,
    title: "Institution's Innovation Council (IIC)",
    desc: "Fostering innovation and entrepreneurship",
    link: "https://rvscas.ac.in/iic/iichome",
  },
  {
    icon: BookOpen,
    title: "E-Content",
    desc: "Access digital learning materials anytime",
    link: "https://rvscas.ac.in/academics/academic-insights/econtents",
  },
]

export default function ExploreMore() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true })

  return (
    <section id="explore-more" className="relative py-20 overflow-hidden">
      <div className="absolute inset-0 bg-[#0a0f1e]/40 backdrop-blur-[2px]" />
      <div ref={ref} className="relative z-10 mx-auto max-w-7xl px-4">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <h2 className="text-2xl md:text-4xl font-bold text-white">
            Explore <span className="text-gradient">More</span>
          </h2>
          <p className="mt-3 text-white/50">Discover all that RVS CAS has to offer</p>
        </motion.div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {items.map((item, i) => (
            <motion.a
              key={i}
              href={item.link || "#"}
              target={item.link ? "_blank" : undefined}
              rel={item.link ? "noopener noreferrer" : undefined}
              initial={{ opacity: 0, y: 30 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.5, delay: i * 0.1 }}
              className="glass rounded-2xl p-6 text-center hover:bg-white/5 transition-all group"
            >
              <div className="w-14 h-14 rounded-xl bg-accent/10 flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform">
                <item.icon className="w-7 h-7 text-accent" />
              </div>
              <h3 className="text-lg font-bold text-white mb-2">{item.title}</h3>
              <p className="text-white/50 text-sm">{item.desc}</p>
            </motion.a>
          ))}
        </div>
      </div>
    </section>
  )
}
