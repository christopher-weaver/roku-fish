"""Regenerate all production art from checked-in source images without network access."""
import art,fish_mesh,dense_turns,marine_animation,formation_frames,waves,cave_and_net,optimize,catalog
if __name__=='__main__':
    fish_mesh.build();dense_turns.build()
    art.build()
    marine_animation.build()
    formation_frames.reserve_navigation()
    waves.build();cave_and_net.build()
    optimize.optimize()
    catalog.catalog()
