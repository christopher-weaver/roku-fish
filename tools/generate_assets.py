"""Regenerate all production art from checked-in source images without network access."""
import art,fish_mesh,optimize,catalog
if __name__=='__main__':
    art.build()
    fish_mesh.build()
    optimize.optimize()
    catalog.catalog()
