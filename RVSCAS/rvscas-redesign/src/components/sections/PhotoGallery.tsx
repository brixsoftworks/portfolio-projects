import { useRef } from "react"
import { motion, useInView } from "framer-motion"
import { ExternalLink, ImageIcon } from "lucide-react"

const galleryImages = [
  { label: "Campus Front", src: "https://rvscas.ac.in/images/gallery/DSC06130.jpg" },
  { label: "Computer Lab", src: "https://rvscas.ac.in/images/gallery/DSC06133.jpg" },
  { label: "Library", src: "https://rvscas.ac.in/images/gallery/DSC06160.jpg" },
  { label: "Sports Ground", src: "https://rvscas.ac.in/images/gallery/DSC06174.jpg" },
  { label: "Auditorium", src: "https://rvscas.ac.in/images/gallery/DSC06230.jpg" },
  { label: "Graduation Day", src: "https://rvscas.ac.in/images/gallery/DSC06235.jpg" },
]

export default function PhotoGallery() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true })

  return (
    <section id="photo-gallery" className="relative py-20 overflow-hidden">
      <div className="absolute inset-0 bg-[#0a0f1e]/40 backdrop-blur-[2px]" />
      <div className="absolute top-1/2 left-1/4 w-[400px] h-[400px] bg-accent/5 rounded-full blur-[100px]" />

      <div ref={ref} className="relative z-10 mx-auto max-w-7xl px-4">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <h2 className="text-2xl md:text-4xl font-bold text-white">
            Photo <span className="text-gradient">Gallery</span>
          </h2>
          <p className="mt-3 text-white/50">A glimpse into campus life at RVS CAS</p>
        </motion.div>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
          {galleryImages.map((img, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={isInView ? { opacity: 1, scale: 1 } : {}}
              transition={{ duration: 0.4, delay: i * 0.06 }}
              className="group relative glass rounded-xl overflow-hidden cursor-pointer aspect-square"
            >
              <div className="w-full h-full flex items-center justify-center">
                <img src={img.src} alt={img.label} className="w-full h-full object-cover" />
              </div>
              <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-end p-3">
                <span className="text-white text-xs font-medium">{img.label}</span>
              </div>
            </motion.div>
          ))}
        </div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={isInView ? { opacity: 1 } : {}}
          transition={{ duration: 0.6, delay: 0.5 }}
          className="text-center mt-8"
        >
          <a
            href="https://rvscas.ac.in/placement/gallery"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 text-accent hover:underline text-sm"
          >
            View Full Gallery <ExternalLink className="w-3.5 h-3.5" />
          </a>
        </motion.div>
      </div>
    </section>
  )
}
