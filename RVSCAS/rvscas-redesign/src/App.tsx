import ThreeBackground from "@/components/ThreeBackground"
import Navbar from "@/components/Navbar"
import HeroSection from "@/components/sections/HeroSection"
import PlacementAcademy from "@/components/sections/PlacementAcademy"
import TeachingLearning from "@/components/sections/TeachingLearning"
import StudentServices from "@/components/sections/StudentServices"
import QuickLinks from "@/components/sections/QuickLinks"
import Highlights from "@/components/sections/Highlights"
import VoiceOfRvscas from "@/components/sections/VoiceOfRvscas"
import ExploreMore from "@/components/sections/ExploreMore"
import PhotoGallery from "@/components/sections/PhotoGallery"
import InfoSection from "@/components/sections/InfoSection"
import Footer from "@/components/sections/Footer"

function App() {
  return (
    <div className="min-h-screen bg-[#0a0f1e]">
      <ThreeBackground />
      <div className="relative z-10">
        <Navbar />
        <HeroSection />
        <PlacementAcademy />
        <TeachingLearning />
        <StudentServices />
        <QuickLinks />
        <Highlights />
        <VoiceOfRvscas />
        <ExploreMore />
        <PhotoGallery />
        <InfoSection />
        <Footer />
      </div>
    </div>
  )
}

export default App
