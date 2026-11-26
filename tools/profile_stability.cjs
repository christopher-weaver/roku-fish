// Production work/allocation windows, not native FPS or Roku heap measurements.
const fs=require('node:fs'),path=require('node:path');
const bin=fs.realpathSync(process.env.BRS_BIN);
const {Interpreter}=require(path.resolve(path.dirname(bin),'../lib/interpreter'));
const call=Interpreter.prototype.visitCall;let active=false,counts={},aa=0,arrays=0,windows=[];
for(const [method,isAA] of [['visitAALiteral',true],['visitArrayLiteral',false]]){
 const original=Interpreter.prototype[method];
 Interpreter.prototype[method]=function(e){if(active){if(isAA)aa++;else arrays++;}return original.call(this,e);};
}
Interpreter.prototype.visitCall=function(e){
 const name=(e.callee?.name?.text??'method').toLowerCase();
 if(name==='reefstabilitywindow'){
  counts={};aa=arrays=0;active=true;
  try{return call.call(this,e);}finally{
   active=false;windows.push({window:windows.length,counts,aa_literals:aa,array_literals:arrays});
   fs.writeFileSync(process.env.PROFILE_OUT,JSON.stringify({scope:'600 real production ticks per window, High density. Host work/allocations, not native timing or retained Roku heap.',windows},null,2)+'\n');
  }
 }
 if(active)counts[name]=(counts[name]??0)+1;
 return call.call(this,e);
};
require('../tests/roku_runner.cjs');
