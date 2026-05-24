import pygame
import sys

pygame.init()

WIDTH = 300
HEIGHT = 200
dis = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Test Capybara Render Types')

dis.fill((170, 215, 81)) # Light green checkerboard color

def draw_capybara_character(cx, cy, y_offset=0, alpha=255, capy_type='leaf'):
    surf = pygame.Surface((60, 60), pygame.SRCALPHA)
    
    # 1. Draw Backpack first if capy_type is 'backpack' (so it's behind/on the back)
    if capy_type == 'backpack':
        # Blue backpack on the back
        pygame.draw.rect(surf, (41, 128, 185), [8, 20, 12, 18], border_radius=3)
        # Small flap
        pygame.draw.rect(surf, (52, 152, 219), [8, 20, 12, 6], border_radius=1)
        # Strap
        pygame.draw.ellipse(surf, (30, 90, 140), [16, 22, 6, 12], 1)
        
    # 2. Body (chubby brown oval)
    pygame.draw.ellipse(surf, (130, 85, 45), [6, 16, 48, 36])
    
    # 3. Head (rounded rectangle/oval at front-right)
    pygame.draw.ellipse(surf, (155, 110, 70), [36, 12, 20, 22])
    
    # 4. Ears (tiny brown circles)
    pygame.draw.circle(surf, (110, 70, 35), (38, 12), 4)
    
    # 5. Snout / Nose area
    pygame.draw.ellipse(surf, (140, 95, 55), [42, 22, 14, 12])
    pygame.draw.circle(surf, (60, 40, 25), (52, 26), 3) # Nose tip
    
    # 6. Eyes: Closed smiling eyes (happy curves)
    pygame.draw.line(surf, (60, 35, 20), (38, 20), (40, 18), 2)
    pygame.draw.line(surf, (60, 35, 20), (40, 18), (42, 20), 2)
    
    pygame.draw.line(surf, (60, 35, 20), (46, 20), (48, 18), 2)
    pygame.draw.line(surf, (60, 35, 20), (48, 18), (50, 20), 2)
    
    # 7. Mouth: Cute smile
    pygame.draw.line(surf, (60, 35, 20), (43, 30), (46, 32), 2)
    pygame.draw.line(surf, (60, 35, 20), (46, 32), (48, 30), 2)
    
    # 8. Legs (four tiny brown stumps)
    pygame.draw.rect(surf, (110, 75, 40), [14, 48, 6, 8], border_radius=2)
    pygame.draw.rect(surf, (110, 75, 40), [24, 48, 6, 8], border_radius=2)
    pygame.draw.rect(surf, (110, 75, 40), [36, 48, 6, 8], border_radius=2)
    pygame.draw.rect(surf, (110, 75, 40), [44, 48, 6, 8], border_radius=2)
    
    # 9. Draw Red Bandana if capy_type is 'bandana'
    if capy_type == 'bandana':
        # Red bandana tied around head (forehead area)
        pygame.draw.polygon(surf, (210, 50, 40), [(36, 15), (48, 13), (52, 17), (40, 19)])
        # Knot/tails at the back left of the head
        pygame.draw.polygon(surf, (190, 40, 30), [(33, 14), (36, 15), (31, 19)])
        pygame.draw.polygon(surf, (190, 40, 30), [(34, 17), (36, 16), (32, 22)])
        
    # 10. Draw Leaf if capy_type is 'leaf'
    elif capy_type == 'leaf':
        # Green leaf on head
        leaf_surf = pygame.Surface((16, 10), pygame.SRCALPHA)
        pygame.draw.ellipse(leaf_surf, (46, 170, 80), [2, 2, 12, 6])
        pygame.draw.line(leaf_surf, (100, 70, 40), (0, 5), (3, 5), 1)
        surf.blit(leaf_surf, (40, 6))

    if alpha < 255:
        surf.set_alpha(alpha)
        
    dis.blit(surf, (int(cx - 30), int(cy - 30 + y_offset)))

# Draw all three capybaras
draw_capybara_character(60, 100, 0, 255, 'bandana')
draw_capybara_character(150, 100, 0, 255, 'leaf')
draw_capybara_character(240, 100, 0, 255, 'backpack')

pygame.display.update()
pygame.image.save(dis, "scratch/capybara_types_output.png")
pygame.quit()
