import re
import sys

def renumber_sections(markdown_content):
    lines = markdown_content.split('\n')
    # Pattern amélioré pour détecter les titres markdown avec ou sans numérotation
    section_pattern = re.compile(r'^(#+)\s+(.*?)$')
    # Pattern spécifique pour détecter et supprimer la numérotation existante
    numbering_pattern = re.compile(r'^\s*\d+(\.\d+)*\s+')
    
    counters = [0] * 6  # Pour les niveaux de titre h1-h6
    result = []
    
    for line in lines:
        match = section_pattern.match(line)
        if match:
            level = len(match.group(1))
            # Extrait le titre complet après les '#'
            title = match.group(2).strip()
            # Supprime explicitement toute numérotation existante (format: "1.2.3 ")
            title = numbering_pattern.sub('', title)
            
            # Réinitialise les compteurs des niveaux inférieurs
            for i in range(level, 6):
                counters[i] = 0
                
            # Incrémente le compteur du niveau actuel
            counters[level-1] += 1
            
            # Génère la nouvelle numérotation
            numbering = '.'.join(str(counters[i]) for i in range(level) if counters[i] > 0)
            
            # Reconstruit la ligne avec la nouvelle numérotation
            result.append(f"{'#' * level} {numbering} {title}")
        else:
            result.append(line)
    
    return '\n'.join(result)

def main():
    if len(sys.argv) < 2:
        print("Usage: python renumber_markdown.py input.md [output.md]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'renumbered_' + input_file
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        renumbered_content = renumber_sections(content)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(renumbered_content)
        
        print(f"Successfully renumbered sections in '{input_file}' and saved to '{output_file}'")
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()