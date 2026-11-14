"""Regenerate all production art from checked-in source images without network access."""
import art,fish_mesh,optimize,catalog
if __name__=='__main__':
    fish_mesh.build()
    art.build()
    optimize.optimize()
    catalog.catalog()
