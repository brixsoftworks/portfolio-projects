import { useRef } from "react"
import { motion, useInView } from "framer-motion"
import { Play, ExternalLink } from "lucide-react"

const videos = [
  { title: "RVS Campus Tour", id: "6Z3jYxlyvww" },
  { title: "Student Testimonials", id: "o36pOEyXsXI" },
  { title: "College Events", id: "cKg1nLoDti8" },
  { title: "Placement Success", id: "B4qBDa97koo" },
]

export default function VoiceOfRvscas() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true })

  return (
    <section id="voice" className="relative py-20 overflow-hidden">
      <div className="absolute inset-0 bg-[#0a0f1e]/40 backdrop-blur-[2px]" />
      <div className="absolute top-0 left-0 w-[400px] h-[400px] bg-primary-light/10 rounded-full blur-[100px]" />

      <div ref={ref} className="relative z-10 mx-auto max-w-7xl px-4">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <h2 className="text-2xl md:text-4xl font-bold text-white">
            Voice of <span className="text-gradient">RVSCAS</span>
          </h2>
          <p className="mt-3 text-white/50">Watch our campus come alive through these videos</p>
        </motion.div>

        <div className="grid sm:grid-cols-2 gap-6">
          {videos.map((video, i) => (
            <motion.a
              key={i}
              href={`https://youtu.be/${video.id}`}
              target="_blank"
              rel="noopener noreferrer"
              initial={{ opacity: 0, y: 30 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.5, delay: i * 0.1 }}
              className="glass rounded-2xl overflow-hidden group block"
            >
              <div className="relative aspect-video bg-gradient-to-br from-primary-light/30 to-primary/30 flex items-center justify-center">
                <div className="w-16 h-16 rounded-full bg-accent/90 flex items-center justify-center group-hover:scale-110 transition-transform group-hover:bg-accent">
                  <Play className="w-7 h-7 text-primary ml-0.5" />
                </div>
                <div className="absolute inset-0 bg-black/20 group-hover:bg-black/10 transition-colors" />
              </div>
              <div className="p-4 flex items-center justify-between">
                <h3 className="text-white font-semibold">{video.title}</h3>
                <ExternalLink className="w-4 h-4 text-white/40 group-hover:text-accent transition-colors" />
              </div>
            </motion.a>
          ))}
        </div>
      </div>
    </section>
  )
}
