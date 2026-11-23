// Count actual production BrightScript calls with the Roku cursor adapter.
// PROFILE_OUT=work/cpu-current.json BRS_BIN=... node tools/profile_updates.cjs
// --root roku roku/source/{math,camera,aquarium,fish,schooling,effects,settings-model}.brs tests/cpu_workload.brs
// Call counts are host evidence of work removed, not an estimate of Roku FPS.
const fs=require('node:fs'),path=require('node:path');
const bin=fs.realpathSync(process.env.BRS_BIN);
const {Interpreter}=require(path.resolve(path.dirname(bin),'../lib/interpreter'));
const original=Interpreter.prototype.visitCall;
let active=false,counts={};
Interpreter.prototype.visitCall=function(expr){
 const name=(expr.callee?.name?.text??'method').toLowerCase();
 if(name==='reefcpuwindow'){
  counts={};active=true;
  try{return original.call(this,expr)}finally{
   active=false;
   fs.writeFileSync(process.env.PROFILE_OUT,JSON.stringify({scope:'Production BrightScript, 60 fixed ticks / 8 fish, excluding startup. Call counts only; not Roku FPS.',counts},null,2)+'\n');
  }
 }
 if(active)counts[name]=(counts[name]??0)+1;
 return original.call(this,expr);
};
require('../tests/roku_runner.cjs');
