import json,random,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from collision_index import make_index,encoded

class CollisionIndexTests(unittest.TestCase):
    def test_shipping_index_is_current(self):
        occ=json.loads((ROOT/'roku/scenes/occupancy.json').read_text())
        self.assertEqual((ROOT/'roku/scenes/collision-index.json').read_text(),encoded(occ))

    def test_all_rectangles_on_irregular_grid(self):
        # Exhaustive rectangles on a non-power-of-two grid, compared with cells.
        rows=['..#......','.........','#.......#','....#....','.........','...#.....','........#']
        table=make_index({'cell':8,'rows':rows,'planes':[{'id':'test','rows':rows}]})
        levels=table['planes'][0]['levels']
        for top in range(len(rows)):
            for bottom in range(top,len(rows)):
                height=bottom-top+1;level=table['levelByHeight'][height]
                last=bottom-table['spanByHeight'][height]+1
                union=[table['masks'][levels[level][r]]for r in [top,last]]
                for left in range(len(rows[0])):
                    for right in range(left,len(rows[0])):
                        expected=any('#'in row[left:right+1]for row in rows[top:bottom+1])
                        actual=any('#'in row[left:right+1]for row in union)
                        self.assertEqual(actual,expected,(left,top,right,bottom))

    def test_every_shipping_query_height(self):
        occ=json.loads((ROOT/'roku/scenes/occupancy.json').read_text());table=make_index(occ)
        rng=random.Random(47831)
        for plane,index in zip(occ['planes'],table['planes']):
            rows=plane['rows']
            for height in range(1,len(rows)+1):
                top=rng.randrange(len(rows)-height+1);bottom=top+height-1
                level=table['levelByHeight'][height];last=bottom-table['spanByHeight'][height]+1
                union=[table['masks'][index['levels'][level][r]]for r in [top,last]]
                for _ in range(3):
                    left=rng.randrange(len(rows[0]));right=rng.randrange(left,len(rows[0]))
                    self.assertEqual(any('#'in r[left:right+1]for r in rows[top:bottom+1]),any('#'in r[left:right+1]for r in union))
