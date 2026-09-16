import { useState, useEffect, useCallback } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Menu, X, ChevronDown, GraduationCap } from "lucide-react"
import { cn } from "@/lib/utils"

type NavChild = { label: string; href: string }

type NavItem = {
  label: string
  href?: string
  children?: NavChild[]
}

const navItems: NavItem[] = [
  { label: "Home", href: "#home" },
  {
    label: "About",
    children: [
      { label: "About College", href: "#highlights" },
      { label: "Vision & Mission", href: "#highlights" },
      { label: "Management", href: "#highlights" },
      { label: "Principal's Message", href: "#highlights" },
      { label: "Accolades & Recognition", href: "#highlights" },
      { label: "Policies", href: "#info" },
    ],
  },
  {
    label: "Academics",
    children: [
      { label: "School of Computer Studies", href: "#highlights" },
      { label: "School of Business Management", href: "#highlights" },
      { label: "School of Science", href: "#highlights" },
      { label: "School of Languages", href: "#highlights" },
      { label: "Academic Insights", href: "#teaching-learning" },
      { label: "E-Content", href: "#explore-more" },
      { label: "Academic Calendar", href: "#info" },
    ],
  },
  {
    label: "Admissions",
    children: [
      { label: "Admission Procedure", href: "#student-services" },
      { label: "Courses Offered", href: "#student-services" },
      { label: "Fee Structure", href: "#student-services" },
      { label: "Online Application", href: "#student-services" },
      { label: "Scholarships", href: "#student-services" },
    ],
  },
  { label: "Placements", href: "#placements" },
  {
    label: "Research",
    children: [
      { label: "Research Policy", href: "#info" },
      { label: "Research Centers", href: "#info" },
      { label: "Publications", href: "#info" },
      { label: "MoU's", href: "#info" },
      { label: "Funded Projects", href: "#info" },
    ],
  },
  {
    label: "Campus Life",
    children: [
      { label: "Infrastructure", href: "#photo-gallery" },
      { label: "Library", href: "#photo-gallery" },
      { label: "Sports", href: "#photo-gallery" },
      { label: "Hostel", href: "#photo-gallery" },
      { label: "Transport", href: "#photo-gallery" },
      { label: "Photo Gallery", href: "#photo-gallery" },
    ],
  },
  { label: "Contact", href: "#contact" },
]

function scrollToSection(href: string) {
  const id = href.replace("#", "")
  const el = document.getElementById(id)
  if (el) {
    el.scrollIntoView({ behavior: "smooth", block: "start" })
  }
}

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)
  const [activeDropdown, setActiveDropdown] = useState<number | null>(null)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 50)
    window.addEventListener("scroll", onScroll)
    return () => window.removeEventListener("scroll", onScroll)
  }, [])

  const handleNavClick = useCallback((e: React.MouseEvent<HTMLAnchorElement>, href?: string) => {
    if (!href || href === "#") return
    e.preventDefault()
    setMobileOpen(false)
    setActiveDropdown(null)
    scrollToSection(href)
  }, [])

  return (
    <motion.nav
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
      className={cn(
        "fixed top-0 left-0 right-0 z-50 transition-all duration-500",
        scrolled ? "glass shadow-lg shadow-black/10" : "bg-[#0a0f1e]/60 backdrop-blur-sm"
      )}
    >
      <div className="mx-auto flex h-18 max-w-7xl items-center justify-between px-4 lg:px-8">
        <a
          href="#home"
          onClick={(e) => handleNavClick(e, "#home")}
          className="flex items-center gap-3 group shrink-0"
        >
          <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-accent text-primary font-bold group-hover:scale-110 transition-transform">
            <GraduationCap className="w-6 h-6" />
          </div>
          <span className="hidden sm:block text-sm lg:text-lg font-bold text-white leading-tight">
            RVS College of
            <br />
            <span className="text-accent">Arts & Science</span>
          </span>
        </a>

        <div className="hidden lg:flex items-center gap-1">
          {navItems.map((item, i) => (
            <div
              key={i}
              className="relative"
              onMouseEnter={() => setActiveDropdown(i)}
              onMouseLeave={() => setActiveDropdown(null)}
            >
              <a
                href={item.href || "#"}
                onClick={(e) => handleNavClick(e, item.href)}
                className="flex items-center gap-1 px-3 py-2 text-sm text-white/70 hover:text-accent rounded-lg hover:bg-white/5 transition-all"
              >
                {item.label}
                {item.children && <ChevronDown className="w-3 h-3" />}
              </a>
              {item.children && activeDropdown === i && (
                <motion.div
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 8 }}
                  className="absolute top-full left-0 glass rounded-xl p-2 min-w-56 shadow-xl"
                >
                  {item.children.map((child, j) => (
                    <a
                      key={j}
                      href={child.href}
                      onClick={(e) => handleNavClick(e, child.href)}
                      className="block px-4 py-2.5 text-sm text-white/70 hover:text-accent hover:bg-white/5 rounded-lg transition-all"
                    >
                      {child.label}
                    </a>
                  ))}
                </motion.div>
              )}
            </div>
          ))}
        </div>

        <button
          className="lg:hidden p-2 text-white"
          onClick={() => setMobileOpen(!mobileOpen)}
        >
          {mobileOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </div>

      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="lg:hidden glass border-t border-white/10 max-h-[80vh] overflow-y-auto"
          >
            <div className="flex flex-col p-4 gap-1">
              {navItems.map((item, i) => (
                <div key={i}>
                  <a
                    href={item.href || "#"}
                    onClick={(e) => handleNavClick(e, item.href)}
                    className="flex items-center justify-between px-4 py-3 text-white/70 hover:text-accent hover:bg-white/5 rounded-lg transition-all"
                  >
                    {item.label}
                    {item.children && <ChevronDown className="w-4 h-4" />}
                  </a>
                  {item.children && (
                    <div className="ml-4 border-l border-white/10 pl-4 mt-1 space-y-1">
                      {item.children.map((child, j) => (
                        <a
                          key={j}
                          href={child.href}
                          onClick={(e) => handleNavClick(e, child.href)}
                          className="block px-4 py-2 text-sm text-white/50 hover:text-accent rounded-lg transition-all"
                        >
                          {child.label}
                        </a>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.nav>
  )
}
