import { GraduationCap, MapPin, Phone, Mail, Video, Camera, MessageCircle, Globe } from "lucide-react"

const footerColumns = [
  {
    title: "Quick Links",
    links: [
      { label: "Download Brochure", href: "https://admissions.rvscas.ac.in/?leadform=Admission_Brochure_cas_website" },
      { label: "Enquiry", href: "https://admissions.rvscas.ac.in/?leadform=Admission_enquiry_cas_website" },
      { label: "Online Admission", href: "https://admissions.rvscas.ac.in/" },
      { label: "Grievance Redressal", href: "https://forms.gle/WeAAx2spWL14xEF68" },
      { label: "E-Governance", href: "https://rvscas.ac.in/examination" },
      { label: "RVS Incubation", href: "#" },
      { label: "Privacy Policy", href: "#" },
    ],
  },
  {
    title: "Mandatory",
    links: [
      { label: "NAAC", href: "https://rvscas.ac.in/naac" },
      { label: "NIRF", href: "https://rvscas.ac.in/nirf" },
      { label: "AICTE", href: "https://rvscas.ac.in" },
      { label: "Bharathiar University", href: "https://b-u.ac.in/" },
      { label: "Mandatory Disclosure", href: "https://rvscas.ac.in" },
      { label: "HR Policy Book", href: "#" },
    ],
  },
  {
    title: "Others",
    links: [
      { label: "NPTEL", href: "https://nptel.ac.in/" },
      { label: "Swayam", href: "https://swayam.gov.in/" },
      { label: "Vidya-Mitra", href: "https://vidyamitra.inflibnet.ac.in/" },
      { label: "Gateway to All PG Courses", href: "http://epgp.inflibnet.ac.in/" },
      { label: "Sakshat (Innovative E-Content)", href: "https://sakshat.ac.in/" },
      { label: "Skill Test For Students", href: "https://www.youth4work.com/onlinetalenttest/" },
    ],
  },
]

export default function Footer() {
  return (
    <footer id="contact" className="relative border-t border-white/10">
      <div className="absolute inset-0 bg-[#0a0f1e]/60 backdrop-blur-[2px]" />
      <div className="mx-auto max-w-7xl px-4 py-16 relative z-10">
        <div className="grid md:grid-cols-2 lg:grid-cols-5 gap-8">
          <div className="lg:col-span-2">
            <div className="flex items-center gap-3 mb-4">
              <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-accent text-primary">
                <GraduationCap className="w-6 h-6" />
              </div>
              <div>
                <span className="text-lg font-bold text-white">RVS College of</span>
                <br />
                <span className="text-accent font-bold">Arts & Science</span>
              </div>
            </div>
            <p className="text-white/40 text-sm leading-relaxed max-w-sm">
              Rathnavel Subramaniam College of Arts and Science (Autonomous).
              Affiliated to Bharathiar University, Coimbatore.
              NAAC A+ Accredited | Since 1986
            </p>

            <div className="mt-6 space-y-3">
              <div className="flex items-start gap-3">
                <MapPin className="w-4 h-4 text-accent mt-0.5" />
                <span className="text-white/50 text-sm">
                  242, Trichy Road, Sulur, Coimbatore, Tamil Nadu, India
                </span>
              </div>
              <div className="flex items-start gap-3">
                <Phone className="w-4 h-4 text-accent mt-0.5" />
                <span className="text-white/50 text-sm">
                  Office: 0422 2687 421 | +91 80121 33444 | +91 97153 74000
                </span>
              </div>
              <div className="flex items-start gap-3">
                <Mail className="w-4 h-4 text-accent mt-0.5" />
                <span className="text-white/50 text-sm">info@rvsgroup.com</span>
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              {[
                { icon: Video, href: "https://youtube.com/c/RVSCASSulurCoimbatore" },
                { icon: Camera, href: "https://www.instagram.com/rvssulur.cas/" },
                { icon: MessageCircle, href: "https://www.facebook.com/rvssulur.cas/" },
                { icon: Globe, href: "https://www.linkedin.com/company/rvssulur-cas/" },
              ].map((social, i) => (
                <a
                  key={i}
                  href={social.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-9 h-9 rounded-lg glass flex items-center justify-center text-white/50 hover:text-accent hover:bg-accent/10 transition-all"
                >
                  <social.icon className="w-4 h-4" />
                </a>
              ))}
            </div>
          </div>

          {footerColumns.map((col, i) => (
            <div key={i}>
              <h4 className="text-white font-semibold mb-4 text-sm uppercase tracking-wider">{col.title}</h4>
              <ul className="space-y-2.5">
                {col.links.map((link, j) => (
                  <li key={j}>
                    <a href={link.href} target="_blank" rel="noopener noreferrer" className="text-white/40 text-sm hover:text-accent transition-colors">
                      {link.label}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="border-t border-white/10 mt-12 pt-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-white/30 text-xs">
            &copy; {new Date().getFullYear()} RVSCAS. All Rights Reserved.
          </p>
          <p className="text-white/20 text-xs">
            Last Updated: 2024
          </p>
        </div>
      </div>
    </footer>
  )
}
