function gvjs_wY(a,b,c,d,e,f){typeof a===gvjs_l?(this.Aj="y"==a?b:0,this.months="m"==a?b:0,this.days="d"==a?b:0,this.hours="h"==a?b:0,this.minutes="n"==a?b:0,this.seconds="s"==a?b:0):(this.Aj=a||0,this.months=b||0,this.days=c||0,this.hours=d||0,this.minutes=e||0,this.seconds=f||0)}gvjs_=gvjs_wY.prototype;
gvjs_.TA=function(a){var b=Math.min(this.Aj,this.months,this.days,this.hours,this.minutes,this.seconds),c=Math.max(this.Aj,this.months,this.days,this.hours,this.minutes,this.seconds);if(0>b&&0<c)return null;if(!a&&0==b&&0==c)return"PT0S";c=[];0>b&&c.push("-");c.push("P");(this.Aj||a)&&c.push(Math.abs(this.Aj)+"Y");(this.months||a)&&c.push(Math.abs(this.months)+"M");(this.days||a)&&c.push(Math.abs(this.days)+"D");if(this.hours||this.minutes||this.seconds||a)c.push("T"),(this.hours||a)&&c.push(Math.abs(this.hours)+
"H"),(this.minutes||a)&&c.push(Math.abs(this.minutes)+"M"),(this.seconds||a)&&c.push(Math.abs(this.seconds)+"S");return c.join("")};gvjs_.equals=function(a){return a.Aj==this.Aj&&a.months==this.months&&a.days==this.days&&a.hours==this.hours&&a.minutes==this.minutes&&a.seconds==this.seconds};gvjs_.clone=function(){return new gvjs_wY(this.Aj,this.months,this.days,this.hours,this.minutes,this.seconds)};
gvjs_.yZ=function(){return new gvjs_wY(-1*this.Aj,-1*this.months,-1*this.days,-1*this.hours,-1*this.minutes,-1*this.seconds)};gvjs_.add=function(a){this.Aj+=a.Aj;this.months+=a.months;this.days+=a.days;this.hours+=a.hours;this.minutes+=a.minutes;this.seconds+=a.seconds};function gvjs_xY(a,b,c,d,e,f,g){this.date=typeof a===gvjs_g?new Date(a,b||0,c||1,d||0,e||0,f||0,g||0):new Date(a&&a.getTime?a.getTime():gvjs_se())}gvjs_t(gvjs_xY,gvjs_Qi);gvjs_=gvjs_xY.prototype;gvjs_.getHours=function(){return this.date.getHours()};
gvjs_.getMinutes=function(){return this.date.getMinutes()};gvjs_.getSeconds=function(){return this.date.getSeconds()};gvjs_.getMilliseconds=function(){return this.date.getMilliseconds()};gvjs_.getUTCDay=function(){return this.date.getUTCDay()};gvjs_.getUTCHours=function(){return this.date.getUTCHours()};gvjs_.getUTCMinutes=function(){return this.date.getUTCMinutes()};gvjs_.getUTCSeconds=function(){return this.date.getUTCSeconds()};gvjs_.getUTCMilliseconds=function(){return this.date.getUTCMilliseconds()};
gvjs_.setHours=function(a){this.date.setHours(a)};gvjs_.setMinutes=function(a){this.date.setMinutes(a)};gvjs_.setSeconds=function(a){this.date.setSeconds(a)};gvjs_.setMilliseconds=function(a){this.date.setMilliseconds(a)};gvjs_.setUTCHours=function(a){this.date.setUTCHours(a)};gvjs_.setUTCMinutes=function(a){this.date.setUTCMinutes(a)};gvjs_.setUTCSeconds=function(a){this.date.setUTCSeconds(a)};gvjs_.setUTCMilliseconds=function(a){this.date.setUTCMilliseconds(a)};
gvjs_.add=function(a){gvjs_Qi.prototype.add.call(this,a);a.hours&&this.setUTCHours(this.date.getUTCHours()+a.hours);a.minutes&&this.setUTCMinutes(this.date.getUTCMinutes()+a.minutes);a.seconds&&this.setUTCSeconds(this.date.getUTCSeconds()+a.seconds)};
gvjs_.TA=function(a){var b=gvjs_Qi.prototype.TA.call(this,a);return a?b+"T"+gvjs_fg(this.getHours(),2)+":"+gvjs_fg(this.getMinutes(),2)+":"+gvjs_fg(this.getSeconds(),2):b+"T"+gvjs_fg(this.getHours(),2)+gvjs_fg(this.getMinutes(),2)+gvjs_fg(this.getSeconds(),2)};gvjs_.equals=function(a){return this.getTime()==a.getTime()};gvjs_.toString=function(){return this.TA()};gvjs_.clone=function(){var a=new gvjs_xY(this.date);a.tC=this.tC;a.uC=this.uC;return a};function gvjs_yY(){}gvjs_o(gvjs_yY,gvjs_zl);
gvjs_yY.prototype.Pb=function(a){try{this.Ac(a)}catch(b){return!1}return!0};gvjs_yY.prototype.Ac=function(a){a=gvjs_Al(a);for(var b=[],c=a.$(),d=0;d<c;++d){var e=a.Jg(d);if(""===e)b.push(new gvjs_6Q(d));else{if(1>b.length)throw Error("At least 1 data column must come before any role column.");gvjs_Ae(b).n3.set(e,d)}}if(2!=b.length)throw Error("Invalid data table format: must have 2 data columns.");c=b[0];b=b[1];this.jb(a,c.index(),"date|datetime");this.jb(a,b.index(),gvjs_g);return{MX:c,eB:b}};
gvjs_yY.prototype.jb=function(a,b,c){if(!gvjs_Fe(c.split("|"),function(d){return gvjs_Dl(a,b,d)},this))throw Error(gvjs_Sa+b+gvjs_ba+c+"'.");};function gvjs_zY(a,b){gvjs_KR.call(this);this.ua=a;this.xa=null;this.Hi=b;this.RY=null;this.dT=new Set;this.KW=new gvjs_9i;this.Yc=new gvjs_Wi(gvjs_Wi.Format.LONG_DATE);this.G7=!1}gvjs_o(gvjs_zY,gvjs_KR);gvjs_=gvjs_zY.prototype;
gvjs_.cW=function(a){var b=gvjs_CL(a.Oa()),c=[];gvjs_u(this.ua.labels,function(d,e){d=b.ys(d.text,d.x,d.y,d.width,d.angle,d.bA,d.dA,d.style);e=gvjs_GL(gvjs_GL(new gvjs_EL(gvjs_0r),gvjs_ks,e),gvjs_ms,gvjs_8c);c.push(new gvjs_JR(d,e,gvjs_Lu))},this);gvjs_u(this.ua.bpa,function(d,e){d=b.Dc(d.vc,d.brush);e=gvjs_GL(gvjs_GL(new gvjs_EL(gvjs_0r),gvjs_ks,e),gvjs_ms,"gridpath");c.push(new gvjs_JR(d,e,gvjs_Lu))},this);gvjs_u(this.ua.Bta,function(d,e){d=b.Dc(d.vc,d.brush);e=gvjs_GL(gvjs_GL(new gvjs_EL(gvjs_0r),
gvjs_ks,e),gvjs_ms,"monthpath");c.push(new gvjs_JR(d,e,gvjs_NQ))},this);return c};
gvjs_.AB=function(a){var b=gvjs_CL(a.Oa()),c=[];this.xa&&(this.ua.$f?gvjs_EG(this.xa,this.Hi.getContainer()):c.push(new gvjs_JR(gvjs_GG(this.xa,b).j(),new gvjs_EL(gvjs_JQ),gvjs_Pd)),this.xa=null);gvjs_u(this.ua.cells,function(d){if(d.dirty){d.dirty=!1;var e=gvjs_GL(gvjs_GL(new gvjs_EL(gvjs_js),"DATE",d.date.getTime()),gvjs_ms,d.date.getTime());null!=d.TS&&gvjs_GL(e,gvjs_ks,d.TS);this.KW.set(d.date.getTime(),d);var f=d.brush,g=gvjs_yw,h=e.ie();if(e.equals(this.RY)||this.dT.has(h))f=this.ua.loa.clone(),
f.Te(d.fillColor),f.mf(1),g=gvjs_ys;d=b.Bl(d.x,d.y,d.width,d.height,f);c.push(new gvjs_JR(d,e,g))}},this);return c};gvjs_.Tb=function(){return this.ua.size};gvjs_.nm=function(a,b,c){var d=this;switch(b.type){case gvjs_Pd:this.bz(a,c);break;case gvjs_tu:gvjs_AY(this,this.RY);gvjs_AY(this,a);this.RY=c?a:null;break;case gvjs_k:this.dT.forEach(function(e){gvjs_AY(d,gvjs_HL(e))}),gvjs_AY(this,a),c?this.dT.add(a.ie()):this.dT.delete(a.ie())}};
function gvjs_AY(a,b){null!=b&&(a.KW.get(b.rb.SUBTYPE).dirty=!0)}
gvjs_.bz=function(a,b){this.Hi.clear();this.xa=null;if(b){a=this.KW.get(a.rb.SUBTYPE);b=this.ua.size;b=new gvjs_B(0,b.width,b.height,0);var c=new gvjs_z(a.x,a.y),d=gvjs_az(c,new gvjs_z(-1,1));if(a.tooltip&&this.ua.$f)a={html:gvjs_5f(gvjs_Ob,{"class":gvjs_Ju},gvjs_KA(a.tooltip.content)),kO:a.tooltip.Nh,pivot:d,anchor:c,HG:b,spacing:20,margin:5};else{var e={entries:[]},f=this.Yc.format(a.date);e.entries.push(gvjs_dG(a.tooltip?a.tooltip.content:""+f+(null!=a.value?": "+a.value:""),this.ua.Dp));a=gvjs_gG(e,
this.ua.sc,!1,c,b,d,void 0,this.ua.$f)}this.xa=a}};function gvjs_BY(a,b,c,d){this.r=a;this.g=b;this.b=c;this.a=d}var gvjs_2ka=new gvjs_BY(0,0,0,1);function gvjs_CY(a){if(!a)return null;try{var b=gvjs_tj(gvjs_oj(a).hex);return new gvjs_BY(b[0]/255,b[1]/255,b[2]/255,1)}catch(c){return null}}gvjs_BY.prototype.um=function(){return[this.r,this.g,this.b,this.a]};gvjs_BY.prototype.multiply=function(a){return new gvjs_BY(gvjs_0g(this.r*a,0,1),gvjs_0g(this.g*a,0,1),gvjs_0g(this.b*a,0,1),this.a)};
gvjs_BY.prototype.equals=function(a){return!!a&&a.r==this.r&&a.g==this.g&&a.b==this.b&&a.a==this.a};var gvjs_DY=["#e7711c",gvjs_Kx,"#4374e0"];function gvjs_EY(){this.C_=[0];this.Kb=[gvjs_2ka];this.Qta=gvjs_CY("#eeeeee")}gvjs_=gvjs_EY.prototype;gvjs_.xT=function(a){this.C_=Array.prototype.slice.call(arguments);return this};gvjs_.ip=function(a){for(var b=[],c=0,d=arguments.length;c<d;++c){var e=b,f=e.push;var g=arguments[c];g=g instanceof gvjs_BY?g:g instanceof Array?4<=g.length?new gvjs_BY(g[0],g[1],g[2],g[3]):new gvjs_BY(g[0],g[1],g[2],1):gvjs_CY(g);f.call(e,g)}this.Kb=b;return this};
gvjs_.getColors=function(){return this.Kb};gvjs_.color=function(a){if(null===a||void 0===a||isNaN(a))return this.Qta;var b=this.C_;if(a<=b[0])return this.Kb[0];for(var c=0,d=b.length-1;c<d;++c)if(b[c]<a&&a<=b[c+1]){d=this.Kb[c];var e=this.Kb[c+1];a=(a-b[c])/(b[c+1]-b[c]);return new gvjs_BY(gvjs_0y(d.r,e.r,a),gvjs_0y(d.g,e.g,a),gvjs_0y(d.b,e.b,a),gvjs_0y(d.a,e.a,a))}return this.Kb[this.Kb.length-1]};gvjs_.Cq=function(a){return gvjs_FY(this.color(a))};
function gvjs_FY(a){a=a.um();for(var b=0;3>b;++b)a[b]=Math.floor(255*a[b]);return gvjs_sj(a)};function gvjs_GY(a){this.ds=new gvjs_A(100,10);this.Oe=null;this.lc=new gvjs_z;this.oh=a}gvjs_GY.prototype.LE=function(a,b){this.lc=new gvjs_z(a,b);return this};gvjs_GY.prototype.Tb=function(){return new gvjs_A(this.ds.width,this.ds.height+this.Oe.fontSize+3)};
gvjs_GY.prototype.$g=function(){for(var a=[],b=this.oh.getColors(),c=b.length-1,d=this.ds.width/c,e=0;e<c;++e){var f=gvjs_4z("green");gvjs_9x(f,{Vf:gvjs_FY(b[e]),sf:gvjs_FY(b[e+1]),tn:null,un:null,x1:0,x2:1,y1:0,y2:0,Sn:!0,sp:!1});var g=new gvjs_OA,h=this.lc.x+e*d,k=this.lc.y+this.Oe.fontSize+3;g.move(h,k);h+=d;g.va(h,k);k+=this.ds.height;g.va(h,k);h-=d;g.va(h,k);g.close();a.push({brush:f,vc:g})}f=gvjs_5z("#eee",1);g=new gvjs_OA;h=this.lc.x;k=this.lc.y+this.Oe.fontSize+3;g.move(h,k);h+=this.ds.width;
g.va(h,k);k+=this.ds.height;g.va(h,k);h-=this.ds.width;g.va(h,k);g.close();a.push({brush:f,vc:g});b=this.EW();return{paths:a,labels:b}};gvjs_GY.prototype.EW=function(){var a=[],b=this.lc.x,c=this.lc.y,d=this.oh.C_,e=d.length,f=this.ds.width/(e-1);gvjs_u(d,function(g,h){var k=gvjs_0;0==h?k=gvjs_2:h==e-1&&(k=gvjs_R);a.push({angle:0,bA:k,dA:gvjs_2,style:this.Oe,text:""+g,width:1,x:b+f*h,y:c})},this);return a};function gvjs_HY(a,b,c){this.lc=new gvjs_z;this.Ww=c;this.Pn=a;this.CU=b}gvjs_=gvjs_HY.prototype;gvjs_.LE=function(a,b){this.lc=new gvjs_z(a,b);return this};gvjs_.setTitle=function(a){this.Pn=a;return this};gvjs_.Tb=function(){var a=this.CU.fontSize,b=this.Ww(this.Pn,this.CU).width;return new gvjs_A(b,a)};gvjs_.$g=function(){return{paths:[],labels:this.EW()}};gvjs_.EW=function(){var a=[];a.push({angle:0,bA:gvjs_2,dA:gvjs_2,style:this.CU,text:this.Pn,width:1,x:this.lc.x,y:this.lc.y});return a};/*

 Copyright The Closure Library Authors.
 SPDX-License-Identifier: Apache-2.0
*/
function gvjs_IY(a,b){this.jga=a;this.XH=b}new gvjs_Qi(0,0,1);new gvjs_Qi(9999,11,31);gvjs_IY.prototype.getStartDate=function(){return this.jga};gvjs_IY.prototype.contains=function(a){return a.valueOf()>=this.jga.valueOf()&&a.valueOf()<=this.XH.valueOf()};gvjs_IY.prototype.iterator=function(){return new gvjs_JY(this)};function gvjs_JY(a){this.z1=a.getStartDate().clone();this.XH=Number(a.XH.TA())}gvjs_t(gvjs_JY,gvjs_3i);
gvjs_JY.prototype.rg=function(){if(Number(this.z1.TA())>this.XH)throw gvjs_2i;var a=this.z1.clone();this.z1.add(new gvjs_wY("d",1));return a};gvjs_JY.prototype.next=gvjs_JY.prototype.rg;function gvjs_KY(a,b,c,d,e,f,g){a=typeof a===gvjs_g?Date.UTC(a,b||0,c||1,d||0,e||0,f||0,g||0):a?a.getTime():gvjs_se();this.date=new Date(a)}gvjs_t(gvjs_KY,gvjs_xY);gvjs_=gvjs_KY.prototype;gvjs_.clone=function(){var a=new gvjs_KY(this.date);a.tC=this.tC;a.uC=this.uC;return a};gvjs_.add=function(a){(a.Aj||a.months)&&gvjs_Qi.prototype.add.call(this,new gvjs_wY(a.Aj,a.months));a=1E3*(a.seconds+60*(a.minutes+60*(a.hours+24*a.days)));this.date=new Date(this.date.getTime()+a)};gvjs_.getTimezoneOffset=function(){return 0};
gvjs_.getFullYear=gvjs_xY.prototype.getUTCFullYear;gvjs_.getMonth=gvjs_xY.prototype.getUTCMonth;gvjs_.getDate=gvjs_xY.prototype.getUTCDate;gvjs_.getHours=gvjs_xY.prototype.getUTCHours;gvjs_.getMinutes=gvjs_xY.prototype.getUTCMinutes;gvjs_.getSeconds=gvjs_xY.prototype.getUTCSeconds;gvjs_.getMilliseconds=gvjs_xY.prototype.getUTCMilliseconds;gvjs_.getDay=gvjs_xY.prototype.getUTCDay;gvjs_.setFullYear=gvjs_xY.prototype.setUTCFullYear;gvjs_.setMonth=gvjs_xY.prototype.setUTCMonth;gvjs_.setDate=gvjs_xY.prototype.setUTCDate;
gvjs_.setHours=gvjs_xY.prototype.setUTCHours;gvjs_.setMinutes=gvjs_xY.prototype.setUTCMinutes;gvjs_.setSeconds=gvjs_xY.prototype.setUTCSeconds;gvjs_.setMilliseconds=gvjs_xY.prototype.setUTCMilliseconds;function gvjs_LY(a,b,c,d){this.Z=a;this.m=b;this.Zd=c;this.eb=d;this.gb=(new gvjs_yY).Ac(a);c=this.Su=gvjs_L(b,"calendar.cellSize");a=new gvjs_hy({});d=7*c;var e=this.Zd;a.om(3*c);var f=e("2222",a);if(f.width<d){for(var g=0;f.width<d;)g=a.fontSize,a.om(g+1),f=e("2222",a);a.om(g)}else for(;f.width>d;)a.om(a.fontSize-1),f=e("2222",a);c=new gvjs_hy({fontSize:Math.max(c-6,5)});d=new gvjs_hy({fontSize:c.fontSize+2});this.PX=gvjs_ny(b,"calendar.dayOfWeekLabel",c);this.IR=gvjs_ny(b,"calendar.monthLabel",
d);this.n6=gvjs_ny(b,"calendar.yearLabel",a);this.Cma=gvjs_L(b,"calendar.dayOfWeekRightSpace");this.Hya=gvjs_L(b,"calendar.underMonthSpace");this.Gya=6;this.$ga=gvjs_L(b,"calendar.underYearSpace");this.m9=gvjs_J(b,"calendar.daysOfWeek");this.mla=gvjs_my(b,"calendar.cellColor");this.gda=gvjs_my(b,"calendar.monthOutlineColor");this.gda.Te(gvjs_f);this.fha=gvjs_my(b,"calendar.unusedMonthOutlineColor");this.fha.Te(gvjs_f);this.h6=gvjs_3ka(this);this.vm=1;this.Fz=this.n6.fontSize+this.$ga+this.h6+this.Cma}
function gvjs_MY(a,b,c,d){var e=new gvjs_KY;e.setTime(a.getTime()-1);e=c(e);d(e);for(a=[];e<b;)a.push(new gvjs_KY(e)),d(e);return a}function gvjs_4ka(a,b){return gvjs_MY(a,b,function(c){return new gvjs_KY(c.getFullYear(),c.getMonth(),c.getDate())},function(c){c.setDate(c.getDate()+1)})}function gvjs_5ka(a,b){return gvjs_MY(a,b,function(c){return new gvjs_KY(c.getFullYear(),c.getMonth(),1)},function(c){c.setMonth(c.getMonth()+1)})}
gvjs_LY.prototype.$g=function(){var a=gvjs_6ka(this),b=a.Zya,c=b.end-b.start;c=this.dR(c?c:1);c=Math.pow(10,c-1);var d=new gvjs_O(Math.floor(b.start/c)*c,Math.ceil(b.end/c)*c);b=this.m;c=b.cD("colorAxis.colors")||gvjs_DY;var e=c===gvjs_DY,f=gvjs_L(b,"colorAxis.minValue",d.start);d=gvjs_L(b,"colorAxis.maxValue",d.end);var g=b.$I("colorAxis.values"),h=0>f&&0<d;if(2>c.length)throw Error("palette.colors must contain at least two values.");2==c.length&&(h=!1);b=new gvjs_EY;if(null!=g){if(c.length!=g.length)throw Error("colorAxis.colors must be the same length as colorAxis.values.");
f=b.xT.apply(b,g);f.ip.apply(f,c)}else if(e)h?(f=Math.max(Math.abs(f),Math.abs(d)),f=b.xT(-f,0,f),c=c.slice(0,3),f.ip.apply(f,c)):(c=0>f?c.slice(0,2):c.slice(-2),f=b.xT(f,d),f.ip.apply(f,c));else{g=[];for(e=0;e<c.length;e++)h=(d-f)/c.length*e,0===e?h=f:e===c.length-1&&(h=d),g.push(h);f=b.xT.apply(b,g);f.ip.apply(f,c)}c=gvjs_J(this.m,gvjs_bx,"");c=(new gvjs_HY(c,this.IR,this.Zd)).LE(this.Fz,this.vm);f=gvjs_x(this.IR);d=this.Su-1;e=new gvjs_GY(b);e.Oe=this.IR;e.ds=new gvjs_A(10*d,d);g=e.Tb();e.LE(this.Fz+
53*this.Su-10*d,this.vm);this.vm+=g.height+this.Gya;f.fontSize=g.height;c.CU=f;e=e.$g();d=c.$g();c=[];f=d.labels;d=d.paths;gvjs_J(this.m,gvjs_qv)!==gvjs_f&&(gvjs_Me(f,e.labels),gvjs_Me(d,e.paths));e=[];g=a.pO.getStartDate().getFullYear();h=a.pO.XH.getFullYear();for(var k=0;g<=h;g++,k++){var l=new gvjs_KY(g,0,1),m=new gvjs_KY(g+1,0,1),n=gvjs_5ka(l,m);0===k&&gvjs_Me(f,gvjs_7ka(this,n,this.Su));var p=l,q=new gvjs_KY(p.getFullYear()+1,p.getMonth(),1,-24);p=gvjs_NY(this,p,q);q=gvjs_ky(this.m,"noDataPattern.color",
gvjs_Rb);var r=gvjs_ky(this.m,"noDataPattern.backgroundColor",gvjs_Rb);q=new gvjs_6x(gvjs_Dw,q,r);r=new gvjs_3;gvjs_8x(r,q);gvjs_Me(e,{brush:r,vc:p});gvjs_Me(f,gvjs_8ka(this,g));gvjs_Me(d,gvjs_9ka(this,a.Cta,n));gvjs_Me(c,gvjs_$ka(this,a.nla,l,m,b));this.vm+=9*this.Su}return{cells:c,labels:f,Bta:d,bpa:e,$f:gvjs_K(this.m,gvjs_jx,!0),Dp:gvjs_ny(this.m,gvjs_lx),loa:gvjs_my(this.m,"calendar.focusedCellColor"),size:this.eb,sc:this.Zd}};
function gvjs_6ka(a){for(var b=new gvjs_9i,c=new Set,d=Number.MAX_VALUE,e=Number.MIN_VALUE,f=a.gb.MX.index(),g=a.gb.eB.index(),h=a.gb.eB.n3.get(gvjs_Jd),k=a.gb.eB.n3.get(gvjs_Pd),l=0,m=a.Z.ca();l<m;l++){var n=a.Z.getValue(l,f),p=new gvjs_KY(n.getFullYear(),n.getMonth(),1);c.add(p.getTime());n=new gvjs_KY(n.getFullYear(),n.getMonth(),n.getDate());p=a.Z.getValue(l,g);d=Math.min(d,p);e=Math.max(e,p);var q=null;h&&(q=a.Z.getValue(l,h),""===q&&(q=null));var r=null;k&&(r=a.Z.getValue(l,k))&&(r={Nh:!(!a.Z.getProperty(l,
k,gvjs_7u)&&!a.Z.Bd(k,gvjs_7u)),content:r});n={color:q,date:n,TS:l,value:p,tooltip:r};b.set(n.date,n)}a=b.ob();gvjs_Qe(a,function(t,u){return gvjs_Jz(t.date,u.date)});g=f=new gvjs_Qi;0<a.length&&(f=a[0].date,g=a[a.length-1].date);return{nla:b,pO:new gvjs_IY(f,g),Cta:c,Zya:new gvjs_O(d,e)}}gvjs_LY.prototype.dR=function(a){return Math.floor(Math.log(Math.abs(a))/Math.log(10))};
function gvjs_OY(a){a=new gvjs_KY(a);for(var b=a.getDate(),c=a.getFullYear(),d=a.getMonth()-1;0<=d;d--)b+=gvjs_Oi(c,d);--b;a=(new gvjs_KY(a.getFullYear(),0,1)).getDay();return Math.floor((b+a%7)/7)}function gvjs_3ka(a){var b=a.Zd,c=a.PX;return gvjs_Ee(a.m9.split(""),function(d,e){e=b(e,c);return Math.max(d,e.width)},0,a)}
function gvjs_$ka(a,b,c,d,e){var f=a.Su;c=gvjs_4ka(c,d);return gvjs_v(c,function(g){var h=g.getDay(),k=gvjs_OY(g),l=b.tf(g)?b.get(g):null,m=l?l.value:null,n=l?l.color:null,p=l?l.TS:null;l=l?l.tooltip:null;var q=this.mla.clone();null!=m?(n=n||e.Cq(m),q.Te(n),q.mf(1)):(n=gvjs_yr,q.Te(n),q.mf(0));return{brush:q,date:g,dirty:!0,tooltip:l,fillColor:n,height:f,TS:p,value:m,width:f,x:this.Fz+k*f,y:this.vm+h*f}},a)}
function gvjs_7ka(a,b,c){b=gvjs_v(b,function(d){var e=new gvjs_KY(d.getFullYear(),d.getMonth()+1,1,-24),f=+gvjs_OY(d);e=+gvjs_OY(e);return{angle:0,bA:gvjs_0,dA:gvjs_2,style:this.IR,text:this.Twa(d),width:(e-f+1)*c,x:this.Fz+(f+e+1)*c/2,y:this.vm}},a);a.vm+=a.PX.fontSize+a.Hya;return b}
function gvjs_8ka(a,b){var c=a.Su,d=7*c,e=[{angle:270,bA:gvjs_0,dA:gvjs_2,style:a.n6,text:""+b,width:d,x:0,y:a.vm+d/2}],f=a.n6.fontSize+a.$ga;gvjs_u(a.m9.split(""),function(g,h){e.push({angle:0,bA:gvjs_0,dA:gvjs_0,style:this.PX,text:g,width:this.h6,x:f+this.h6/2,y:this.vm+h*c+c/2})},a);return e}
function gvjs_9ka(a,b,c){var d=[],e=[];gvjs_u(c,function(f){var g=new gvjs_KY(f.getFullYear(),f.getMonth()+1,1,-24);g=gvjs_NY(this,f,g);b.has(f.getTime())?e.push({brush:this.gda,vc:g}):d.push({brush:this.fha,vc:g})},a);gvjs_Me(d,e);return d}
function gvjs_NY(a,b,c){var d=+b.getDay();b=+gvjs_OY(b);var e=+c.getDay();c=+gvjs_OY(c);var f=a.Su,g=a.vm;a=a.Fz;var h=new gvjs_OA,k=g+d*f;h.move((b+1)*f+a,k);d=b*f+a;h.va(d,k);k=g+7*f;h.va(d,k);d=c*f+a;h.va(d,k);k=g+(e+1)*f;h.va(d,k);d=(c+1)*f+a;h.va(d,k);k=g+0;h.va(d,k);h.va((b+1)*f+a,k);h.close();return h}var gvjs_PY=new gvjs_Rj({pattern:"MMM"});gvjs_LY.prototype.Twa=gvjs_s(gvjs_PY.Ob,gvjs_PY);function gvjs_QY(a){gvjs_QL.call(this,a)}gvjs_o(gvjs_QY,gvjs_QL);gvjs_=gvjs_QY.prototype;gvjs_.xq=function(){return{DATE:gvjs_Lb,ROW_INDEX:gvjs_Cd}};
gvjs_.og=function(){return{backgroundColor:{fill:gvjs_yr,stroke:gvjs_hr,strokeWidth:10,strokeOpacity:.2},tooltip:{isHtml:!0,textStyle:{fontName:gvjs__r,fontSize:"16",color:gvjs_nt}},calendar:{cellColor:{stroke:gvjs_yr,strokeOpacity:1,strokeWidth:1},cellSize:16,dayOfWeekLabel:{fontName:gvjs_zw,color:"#888",bold:!1,italic:!1},dayOfWeekRightSpace:4,daysOfWeek:"SMTWTFS",focusedCellColor:{stroke:gvjs_hr,strokeOpacity:1,strokeWidth:2},monthLabel:{fontName:gvjs_zw,color:"#888",bold:!1,italic:!1},monthOutlineColor:{stroke:gvjs_hr,
strokeOpacity:1,strokeWidth:1},underMonthSpace:6,underYearSpace:0,unusedMonthOutlineColor:{stroke:"#c9c9c9",strokeOpacity:1,strokeWidth:1},yearLabel:{fontName:gvjs_zw,color:"#dfdfdf",bold:!1,italic:!1}},noDataPattern:{backgroundColor:"#ddd",color:"#f8f8f8"},legend:{position:gvjs_j}}};gvjs_.po=function(a,b,c,d){a=gvjs_QL.prototype.po.call(this,a,b,c,d);a.$t([gvjs_Lu,gvjs_yw,gvjs_NQ,gvjs_zs,gvjs_ys,gvjs_Pd]);return a};gvjs_.Mm=function(a,b){return new gvjs_zY(a,b)};
gvjs_.Al=function(a,b,c,d){return new gvjs_LY(a,b,c,d)};gvjs_.xs=function(){return[new gvjs_FR([new gvjs_EL(gvjs_js)]),new gvjs_IR([new gvjs_EL(gvjs_js)]),new gvjs_HR([new gvjs_EL(gvjs_js)])]};gvjs_q("google.visualization.Calendar",gvjs_QY,void 0);gvjs_QY.prototype.draw=gvjs_QY.prototype.draw;gvjs_QY.prototype.setSelection=gvjs_QY.prototype.setSelection;gvjs_QY.prototype.getSelection=gvjs_QY.prototype.getSelection;gvjs_QY.prototype.clearChart=gvjs_QY.prototype.Jb;gvjs_QY.prototype.getContainer=gvjs_QY.prototype.getContainer;gvjs_QY.prototype.getDefaultOptions=gvjs_QY.prototype.og;
