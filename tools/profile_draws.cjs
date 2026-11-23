// Count production renderer calls in the 120-frame swim_sway fixture.
// PROFILE_OUT=work/draw-current.json BRS_BIN=... node tools/profile_draws.cjs
// --root roku roku/source/{math,camera,renderer}.brs tests/swim_sway.brs
// Counts include fixture setup/assertions; these are not GPU timings or Roku FPS.
const fs=require('node:fs'),path=require('node:path');
const bin=fs.realpathSync(process.env.BRS_BIN);
const {Interpreter}=require(path.resolve(path.dirname(bin),'../lib/interpreter'));
const original=Interpreter.prototype.visitCall,counts={};
Interpreter.prototype.visitCall=function(expr){
 const name=(expr.callee?.name?.text??'method').toLowerCase();
 counts[name]=(counts[name]??0)+1;
 return original.call(this,expr);
};
process.on('exit',()=>fs.writeFileSync(process.env.PROFILE_OUT,JSON.stringify({scope:'Production renderer, 120 swim frames; includes fixture setup/assertions. Counts only, not GPU timing or Roku FPS.',counts},null,2)+'\n'));
require('../tests/roku_runner.cjs');
