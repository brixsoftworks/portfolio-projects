import { useRef } from "react"
import { motion, useInView } from "framer-motion"
import { CreditCard, GraduationCap, FileText, ExternalLink } from "lucide-react"

const services = [
  {
    icon: CreditCard,
    title: "On-Line Fee Payment",
    desc: "Pay your fees securely online through our payment portal.",
    link: "https://pay.webfront.in/webfront/#/merchantinfo/rathnavel-subramaniam-educational-trust/6331",
  },
  {
    icon: GraduationCap,
    title: "Online Admission",
    desc: "Apply for UG & PG programs through our online admission portal.",
    link: "https://admissions.rvscas.ac.in/",
  },
  {
    icon: CreditCard,
    title: "Online Graduation Fee Payment",
    desc: "Pay graduation fees conveniently through online mode.",
    link: "https://pay.webfront.in/#/merchantinfo/rathnavel-subramaniam-educational-trust/8224",
  },
  {
    icon: FileText,
    title: "Certificate Verification",
    desc: "Verify your certificates through our online verification system.",
    link: "https://rvscas.directverify.in/student/#/app/request",
  },
]

export default function StudentServices() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true })

  return (
    <section id="student-services" className="relative py-20 overflow-hidden">
      <div className="absolute inset-0 bg-[#0a0f1e]/40 backdrop-blur-[2px]" />
      <div className="absolute top-1/3 right-0 w-[400px] h-[300px] bg-primary-light/10 rounded-full blur-[100px]" />

      <div ref={ref} className="relative z-10 mx-auto max-w-7xl px-4">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <h2 className="text-2xl md:text-4xl font-bold text-white">
            Student <span className="text-gradient">Services</span>
          </h2>
          <p className="mt-3 text-white/50">
            Everything you need, all in one place
          </p>
        </motion.div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {services.map((service, i) => (
            <motion.a
              key={i}
              href={service.link}
              target="_blank"
              rel="noopener noreferrer"
              initial={{ opacity: 0, y: 30 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.5, delay: i * 0.1 }}
              className="glass rounded-2xl p-6 text-center hover:bg-white/5 transition-all group block"
            >
              <div className="w-14 h-14 rounded-xl bg-accent/10 flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform">
                <service.icon className="w-7 h-7 text-accent" />
              </div>
              <h3 className="text-lg font-bold text-white mb-2">{service.title}</h3>
              <p className="text-white/50 text-sm mb-4">{service.desc}</p>
              <span className="inline-flex items-center gap-1 text-accent text-sm font-medium group-hover:underline">
                Access Now <ExternalLink className="w-3 h-3" />
              </span>
            </motion.a>
          ))}
        </div>
      </div>
    </section>
  )
}
