#!/bin/bash
# Replacement downloads for failed images
BASE="/home/mullainathan/projects/nilambur-teak-wood/public"
RESULTS_FILE="/home/mullainathan/projects/nilambur-teak-wood/download_results.log"

download() {
  local url="$1"
  local output="$2"
  local desc="$3"
  echo "Downloading: $desc"
  if curl -L -f -s --max-time 30 "$url" -o "$output" 2>/dev/null; then
    local size=$(stat -c%s "$output" 2>/dev/null || echo "0")
    if [ "$size" -gt 5000 ]; then
      echo "SUCCESS|$output|$url|$desc|$size" >> "$RESULTS_FILE"
      echo "  [OK] Downloaded ($size bytes)"
    else
      rm -f "$output"
      echo "  [X] Too small"
    fi
  else
    rm -f "$output"
    echo "  [X] Failed"
  fi
}

# bedroom-2: Try a different bedroom photo  
download "https://images.unsplash.com/photo-1540518614846-7eded433c457?w=1200&q=80&auto=format" \
  "$BASE/images/bedrooms/bedroom-2.jpg" "Bedroom with warm wood tones"

# wardrobe-1: Try closet/wardrobe alternative
download "https://images.unsplash.com/photo-1556020685-ae41abfc9365?w=1200&q=80&auto=format" \
  "$BASE/images/wardrobes/wardrobe-1.jpg" "Walk-in wardrobe alternative"

# wardrobe-3: Another wardrobe option
download "https://images.unsplash.com/photo-1616486029423-aaa4789e8c9a?w=1200&q=80&auto=format" \
  "$BASE/images/wardrobes/wardrobe-3.jpg" "Modern closet interior"

# door-2: Try different door photo
download "https://images.unsplash.com/photo-1509644851169-2acc08aa25b5?w=1200&q=80&auto=format" \
  "$BASE/images/doors/door-2.jpg" "Classic wooden door"

# staircase-3: Spiral staircase alternative
download "https://images.unsplash.com/photo-1585128792020-803d29415281?w=1200&q=80&auto=format" \
  "$BASE/images/staircases/staircase-3.jpg" "Spiral staircase wood"

# teak-grain texture
download "https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=1024&q=90&auto=format&fit=crop" \
  "$BASE/textures/wood/teak-grain.jpg" "Teak grain texture alt"

# light-wood texture
download "https://images.unsplash.com/photo-1543005680-0f4e1d5c32a5?w=1024&q=80&auto=format" \
  "$BASE/textures/wood/light-wood.jpg" "Light wood texture alt"

# wood-panel texture
download "https://images.unsplash.com/photo-1588854337236-6889d631faa8?w=1024&q=80&auto=format" \
  "$BASE/textures/wood/wood-panel.jpg" "Wood panel texture alt"

echo "=== REPLACEMENTS DONE ==="
