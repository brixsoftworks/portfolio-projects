import { useRef } from "react"
import { motion, useInView } from "framer-motion"
import { BookOpen, Monitor, Users, Target, CheckCircle } from "lucide-react"
import { ExternalLink } from "lucide-react"

const features = [
  {
    icon: BookOpen,
    title: "Industry-Relevant Curriculum",
    desc: "Courses designed to meet the demands of current and future industry needs.",
  },
  {
    icon: Monitor,
    title: "Digital Learning",
    desc: "E-Content, online resources, and digital classrooms for enhanced learning.",
  },
  {
    icon: Users,
    title: "Expert Faculty",
    desc: "Dedicated team with decades of teaching and research experience.",
  },
  {
    icon: Target,
    title: "Skill Development",
    desc: "Career-oriented programs with focus on employability skills.",
  },
]

export default function TeachingLearning() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true })

  return (
    <section id="teaching-learning" className="relative py-20 overflow-hidden">
      <div className="absolute inset-0 bg-[#0a0f1e]/40 backdrop-blur-[2px]" />
      <div className="absolute bottom-0 left-0 w-[500px] h-[500px] bg-accent/5 rounded-full blur-[120px]" />

      <div ref={ref} className="relative z-10 mx-auto max-w-7xl px-4">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <h2 className="text-2xl md:text-4xl font-bold text-white">
            Teaching <span className="text-gradient">Learning Process</span>
          </h2>
          <p className="mt-3 text-white/50 max-w-2xl mx-auto">
            Adopting best practices in education with technology integration and industry collaboration
          </p>
        </motion.div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 30 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.5, delay: i * 0.1 }}
              className="glass rounded-2xl p-6 text-center hover:bg-white/5 transition-all group"
            >
              <div className="w-14 h-14 rounded-xl bg-accent/10 flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform">
                <feature.icon className="w-7 h-7 text-accent" />
              </div>
              <h3 className="text-lg font-bold text-white mb-2">{feature.title}</h3>
              <p className="text-white/50 text-sm leading-relaxed">{feature.desc}</p>
            </motion.div>
          ))}
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, delay: 0.5 }}
          className="mt-10 glass rounded-2xl p-6 md:p-8"
        >
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-xl bg-secondary/20 flex items-center justify-center shrink-0">
              <CheckCircle className="w-6 h-6 text-secondary" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white mb-2">
                Best Practice: Industry Experts as Adjunct Faculty
              </h3>
              <p className="text-white/50 text-sm leading-relaxed">
                The learning approach develops lifelong learning behavior in students.
                SMEs are trained to use the best tools and technologies in the Industry,
                making it easier to incorporate that in the teaching & learning process.
                Adopting and implementing the Best Practice in other institutions.
              </p>
              <a href="https://rvscas.ac.in/academics/academic-insights/bestpractice" target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1 text-accent text-sm mt-3 hover:underline">
                Learn More <ExternalLink className="w-3 h-3" />
              </a>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
