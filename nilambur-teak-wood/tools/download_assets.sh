#!/bin/bash
# Asset download script for Nilambur Teak Wood luxury website
# All images from Unsplash (Unsplash License - free for commercial use)
# Using direct image URLs with size parameters

BASE="/home/mullainathan/projects/nilambur-teak-wood/public"
RESULTS_FILE="/home/mullainathan/projects/nilambur-teak-wood/download_results.log"
echo "" > "$RESULTS_FILE"

download() {
  local url="$1"
  local output="$2"
  local desc="$3"
  echo "Downloading: $desc -> $output"
  if curl -L -f -s --max-time 30 "$url" -o "$output" 2>/dev/null; then
    local size=$(stat -c%s "$output" 2>/dev/null || echo "0")
    if [ "$size" -gt 5000 ]; then
      echo "SUCCESS|$output|$url|$desc|$size" >> "$RESULTS_FILE"
      echo "  [OK] Downloaded ($size bytes)"
    else
      echo "FAIL_SMALL|$output|$url|$desc|$size" >> "$RESULTS_FILE"
      echo "  [X] Too small ($size bytes), removing"
      rm -f "$output"
    fi
  else
    echo "FAIL|$output|$url|$desc|0" >> "$RESULTS_FILE"
    echo "  [X] Download failed"
    rm -f "$output"
  fi
}

echo "=== HERO IMAGES ==="
# Luxury modern home exterior/interior - dramatic
download "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=1920&q=80&auto=format" \
  "$BASE/images/hero/hero-1.jpg" "Luxury modern home exterior"
# Luxury interior living space with warm lighting
download "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=1920&q=80&auto=format" \
  "$BASE/images/hero/hero-2.jpg" "Luxury home interior warm"
# Elegant wooden interior architecture
download "https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?w=1920&q=80&auto=format" \
  "$BASE/images/hero/hero-3.jpg" "Luxury wooden architecture"

echo "=== LIVING ROOMS ==="
# Premium modern living room
download "https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?w=1200&q=80&auto=format" \
  "$BASE/images/living-rooms/living-1.jpg" "Modern luxury living room"
# Warm wood-tone living space  
download "https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?w=1200&q=80&auto=format" \
  "$BASE/images/living-rooms/living-2.jpg" "Warm wood living space"
# Elegant living room with wooden elements
download "https://images.unsplash.com/photo-1616486338812-3dadae4b4ace?w=1200&q=80&auto=format" \
  "$BASE/images/living-rooms/living-3.jpg" "Elegant living room wood elements"

echo "=== KITCHENS ==="
# Luxury modern kitchen
download "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=1200&q=80&auto=format" \
  "$BASE/images/kitchens/kitchen-1.jpg" "Luxury modern kitchen"
# Wooden kitchen cabinets
download "https://images.unsplash.com/photo-1556185781-a47769abb7ee?w=1200&q=80&auto=format" \
  "$BASE/images/kitchens/kitchen-2.jpg" "Wooden kitchen cabinets premium"
# Kitchen with island and wood accents
download "https://images.unsplash.com/photo-1600585152220-90363fe7e115?w=1200&q=80&auto=format" \
  "$BASE/images/kitchens/kitchen-3.jpg" "Kitchen island wood accents"

echo "=== BEDROOMS ==="
# Luxury bedroom with moody lighting
download "https://images.unsplash.com/photo-1616594039964-ae9021a400a0?w=1200&q=80&auto=format" \
  "$BASE/images/bedrooms/bedroom-1.jpg" "Luxury bedroom moody lighting"
# Modern bedroom wooden headboard
download "https://images.unsplash.com/photo-1522771739493-f49e84eeff2d?w=1200&q=80&auto=format" \
  "$BASE/images/bedrooms/bedroom-2.jpg" "Modern bedroom wooden accents"
# Elegant bedroom with wood paneling
download "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=1200&q=80&auto=format" \
  "$BASE/images/bedrooms/bedroom-3.jpg" "Bedroom with wood paneling"

echo "=== WARDROBES ==="
# Walk-in closet / wardrobe
download "https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=1200&q=80&auto=format" \
  "$BASE/images/wardrobes/wardrobe-1.jpg" "Walk-in wardrobe closet"
# Modern wardrobe system
download "https://images.unsplash.com/photo-1595428774223-ef52624120d2?w=1200&q=80&auto=format" \
  "$BASE/images/wardrobes/wardrobe-2.jpg" "Modern wardrobe system"
# Custom built-in closet
download "https://images.unsplash.com/photo-1631048500484-1e834d978561?w=1200&q=80&auto=format" \
  "$BASE/images/wardrobes/wardrobe-3.jpg" "Custom built-in closet"

echo "=== FURNITURE ==="
# Designer teak furniture
download "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=1200&q=80&auto=format" \
  "$BASE/images/furniture/furniture-1.jpg" "Designer sofa luxury"
# Wooden dining table
download "https://images.unsplash.com/photo-1617806118233-18e1de247200?w=1200&q=80&auto=format" \
  "$BASE/images/furniture/furniture-2.jpg" "Wooden dining table premium"
# Handcrafted wooden furniture
download "https://images.unsplash.com/photo-1506439773649-6e0eb8cfb237?w=1200&q=80&auto=format" \
  "$BASE/images/furniture/furniture-3.jpg" "Handcrafted wooden chair"

echo "=== DOORS ==="
# Premium wooden door
download "https://images.unsplash.com/photo-1517466787929-bc90951d0974?w=1200&q=80&auto=format" \
  "$BASE/images/doors/door-1.jpg" "Premium wooden door"
# Ornate wooden door
download "https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=1200&q=80&auto=format" \
  "$BASE/images/doors/door-2.jpg" "Ornate wooden door"
# Modern wooden door
download "https://images.unsplash.com/photo-1534430480872-3498386e7856?w=1200&q=80&auto=format" \
  "$BASE/images/doors/door-3.jpg" "Modern wooden door interior"

echo "=== STAIRCASES ==="
# Luxury wooden staircase
download "https://images.unsplash.com/photo-1572120360610-d971b9d7767c?w=1200&q=80&auto=format" \
  "$BASE/images/staircases/staircase-1.jpg" "Luxury wooden staircase"
# Modern wood staircase interior
download "https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=1200&q=80&auto=format" \
  "$BASE/images/staircases/staircase-2.jpg" "Modern home staircase"
# Spiral wooden staircase
download "https://images.unsplash.com/photo-1545127398-3ef2a0e72e78?w=1200&q=80&auto=format" \
  "$BASE/images/staircases/staircase-3.jpg" "Spiral wooden staircase"

echo "=== MATERIALS / TEXTURES ==="
# Teak wood grain close-up
download "https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=1024&q=80&auto=format" \
  "$BASE/textures/wood/teak-grain.jpg" "Teak wood grain texture"
# Dark wood texture
download "https://images.unsplash.com/photo-1541123603104-512919d6a96c?w=1024&q=80&auto=format" \
  "$BASE/textures/wood/dark-wood.jpg" "Dark wood texture"
# Light wood texture
download "https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=1024&q=80&auto=format" \
  "$BASE/textures/wood/light-wood.jpg" "Light wood texture"
# Wood panel texture
download "https://images.unsplash.com/photo-1548781544-e083fe09b3ea?w=1024&q=80&auto=format" \
  "$BASE/textures/wood/wood-panel.jpg" "Wood panel texture"
# Natural wood surface
download "https://images.unsplash.com/photo-1520038410233-7141be7e6f97?w=1024&q=80&auto=format" \
  "$BASE/images/materials/material-1.jpg" "Natural wood surface texture"
# Wood grain detailed  
download "https://images.unsplash.com/photo-1503708928676-1cb796a0891e?w=1024&q=80&auto=format" \
  "$BASE/images/materials/material-2.jpg" "Detailed wood grain"
# Wooden floor texture
download "https://images.unsplash.com/photo-1622372738946-62e02505feb3?w=1024&q=80&auto=format" \
  "$BASE/images/materials/material-3.jpg" "Wooden floor texture"

echo "=== PORTFOLIO / ADDITIONAL ==="
# Luxury home portfolio shots
download "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=1200&q=80&auto=format" \
  "$BASE/images/portfolio/portfolio-1.jpg" "Luxury home exterior"
download "https://images.unsplash.com/photo-1600573472550-8090b5e0745e?w=1200&q=80&auto=format" \
  "$BASE/images/portfolio/portfolio-2.jpg" "Premium interior design"
download "https://images.unsplash.com/photo-1600585153490-76fb20a32601?w=1200&q=80&auto=format" \
  "$BASE/images/portfolio/portfolio-3.jpg" "Luxury room design"

echo ""
echo "=== DOWNLOAD COMPLETE ==="
echo "Results saved to: $RESULTS_FILE"

# Summary
TOTAL=$(wc -l < "$RESULTS_FILE")
SUCCESS=$(grep -c "^SUCCESS" "$RESULTS_FILE" || echo 0)
FAILED=$(grep -c "^FAIL" "$RESULTS_FILE" || echo 0)
echo "Total attempts: $TOTAL"
echo "Successful: $SUCCESS"
echo "Failed: $FAILED"
