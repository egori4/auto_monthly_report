var gvjs_TY="gantt.barCornerRadius",gvjs_UY="hAxis.position";function gvjs_VY(){this.xy=null}gvjs_o(gvjs_VY,gvjs_Al);gvjs_VY.prototype.Pb=function(a){return!!gvjs_WY(this,a)};gvjs_VY.prototype.Ac=function(a){a=gvjs_WY(this,a);if(null!=a)return a;throw Error(this.xy);};
function gvjs_WY(a,b){b=gvjs_Bl(b);var c=new gvjs_7Q(0),d=new gvjs_7Q(1),e=new gvjs_7Q(2),f=0;gvjs_El(b,e.index(),gvjs_l)||(f=-1,e=null);var g=new gvjs_7Q(3+f),h=new gvjs_7Q(4+f),k=new gvjs_7Q(5+f),l=new gvjs_7Q(6+f);f=new gvjs_7Q(7+f);return a.jb(b,c.index(),gvjs_l)&&a.jb(b,d.index(),gvjs_l)&&a.jb(b,g.index(),gvjs_Mb)&&a.jb(b,h.index(),gvjs_Mb)&&a.jb(b,k.index(),gvjs_g)&&a.jb(b,l.index(),gvjs_g)&&a.jb(b,f.index(),gvjs_l)?{Bra:c,qw:d,vL:g,WH:h,pna:k,Tua:l,Nma:f,Wea:e}:null}
gvjs_VY.prototype.jb=function(a,b,c){return gvjs_El(a,b,c)?!0:(this.xy=gvjs_Ta+b+gvjs_ba+c+"'.",!1)};
var gvjs_XY={50:"#FAFAFA",100:"#F5F5F5",200:"#EEEEEE",300:"#E0E0E0",400:"#BDBDBD",500:"#9E9E9E",600:gvjs_or,700:"#616161",800:"#424242",900:"#212121"},gvjs_ala=[{color:gvjs_PF[gvjs_Qr],dark:gvjs_PF[gvjs_Tr],light:gvjs_PF[gvjs_Mr]},{color:gvjs_QF[gvjs_Qr],dark:gvjs_QF[gvjs_Ur],light:gvjs_QF[gvjs_Mr]},{color:gvjs_RF[gvjs_Rr],dark:gvjs_RF[gvjs_Tr],light:gvjs_RF[gvjs_Mr]},{color:gvjs_SF[gvjs_Qr],dark:gvjs_SF[gvjs_Sr],light:gvjs_SF[gvjs_Mr]},{color:gvjs_TF[gvjs_Pr],dark:gvjs_TF[gvjs_Tr],light:gvjs_TF[gvjs_Mr]},
{color:gvjs_UF[gvjs_Rr],dark:gvjs_UF[gvjs_Tr],light:gvjs_UF[gvjs_Mr]},{color:gvjs_VF[gvjs_Pr],dark:gvjs_VF[gvjs_Sr],light:gvjs_VF[gvjs_Mr]},{color:gvjs_WF[gvjs_Tr],dark:gvjs_WF[gvjs_Ur],light:gvjs_WF[gvjs_Mr]},{color:gvjs_XF[gvjs_Pr],dark:gvjs_XF[gvjs_Rr],light:gvjs_XF[gvjs_Mr]},{color:gvjs_YF["300"],dark:gvjs_YF[gvjs_Qr],light:gvjs_YF[gvjs_Mr]},{color:gvjs_ZF[gvjs_Sr],dark:gvjs_ZF[gvjs_Ur],light:gvjs_ZF[gvjs_Mr]},{color:gvjs_YF[gvjs_Sr],dark:gvjs_YF[gvjs_Ur],light:gvjs_YF["200"]}];
function gvjs_YY(a){this.A1=0;this.oh=a.fa("gantt.palette",gvjs_ala);this.qa=new Map}gvjs_YY.prototype.Sz=function(a){var b=this.oh[a];if(gvjs_r(b))a=b;else{var c=this.oh;var d=gvjs_uj(b);d=gvjs_tj(gvjs_Zz(d,.15));var e=gvjs_uj(b);e=gvjs_tj(gvjs__z(e,.07));a=c[a]={color:b,dark:d,light:e}}return a};gvjs_YY.prototype.color=function(a){return this.Sz(a).color};gvjs_YY.prototype.qb=function(a){return this.Sz(a).dark};gvjs_YY.prototype.jh=function(a){return this.Sz(a).light};function gvjs_ZY(a,b,c,d,e,f,g,h,k){this.ac=b;this.Ei=c;this.Xd=d;this.yf=e;this.Nk=f;this.jea=g;this.Oma=h||[];this.NA=[];this.Vw=[];this.zn=this.error=null;this.yi=a;this.qH=!1;this.Xea=null!=k?k:"";this.UB=0}gvjs_ZY.prototype.getId=function(){return this.ac};gvjs_ZY.prototype.setStart=function(a){this.Xd=a};gvjs_ZY.prototype.getName=function(){return this.Ei};gvjs_ZY.prototype.qP=function(){return this.Oma};
function gvjs_bla(a){var b=gvjs_Fe(a.NA,function(c,d){return null===c?d.yf:Math.max(c,d.yf)},null);if(null===b)throw Error("Cannot compute start time from dependencies for task: "+a.ac);a.Xd=new Date(b);a.yf=new Date(a.Xd.getTime()+a.Nk)};function gvjs__Y(){this.X4=new Map}gvjs__Y.prototype.sB=function(a){this.X4.set(a.getId(),a)};gvjs__Y.prototype.sort=function(a){var b=gvjs_0Y(this),c=gvjs_1Y(b);gvjs_2Y(c,a);gvjs_3Y(c);for(a=0;a<b.length;a++)gvjs_Re(b[a].NA,gvjs_4Y);c=gvjs_cla(c);if(c.length!=b.length)throw Error("Cycle detected.");return c};function gvjs_2Y(a,b){if(null!=b)for(var c=0;c<a.length;c++){var d=a[c];null==d.Xd&&d.setStart(b)}}
function gvjs_0Y(a){for(var b=[].concat(gvjs_$d(a.X4.values())),c=0;c<b.length;c++)for(var d=b[c],e=d.qP(),f=0;f<e.length;f++){var g=e[f],h=a.X4.get(g);if(null==h)throw"Missing dependency '"+g+" in task ${task.getId()}.";d.NA.push(h);h.Vw.push(d)}return b}function gvjs_1Y(a){return a.filter(function(b){return 0==b.NA.length})}
function gvjs_3Y(a){for(var b=new gvjs_Wk,c=new Set,d=0;d<a.length;d++){var e=a[d];b.enqueue(e);c.add(e)}for(;!b.isEmpty();){a=gvjs_Rx(b);d=a.Vw;for(e=0;e<d.length;e++){var f=d[e];if(!c.has(f)){for(var g=!0,h=f.NA,k=0;k<h.length;k++){var l=h[k];if(l!=a){var m=null!=l.Xd,n=null!=l.yf;null!=l.Nk&&m&&n||(g=!1)}}g&&(c.add(f),b.enqueue(f))}}d=null!=a.Xd;e=null!=a.yf;f=null!=a.Nk;if(!f||d||e)if(d&&e)f?a.Nk!=a.yf.getTime()-a.Xd.getTime()&&(a.error="Duration not equal to end time minus start time."):a.Nk=
a.yf.getTime()-a.Xd.getTime();else if(d)if(f)a.yf=new Date(a.Xd.getTime()+a.Nk);else throw Error("Missing duration or end time for task: "+a.ac);else if(e)if(f)a.Xd=new Date(a.yf.getTime()-a.Nk);else throw Error("Missing duration or start time for task: "+a.ac);else throw Error("Cannot compute start/end times for task: "+a.ac);else gvjs_bla(a)}}function gvjs_4Y(a,b){var c=a.Xd,d=b.Xd;if(c<d)return-1;if(c>d)return 1;a=a.Vw.length;b=b.Vw.length;return a<b?-1:a>b?1:0}
function gvjs_cla(a){function b(f,g){var h=g.NA.every(function(k){return d.has(k)});if((null===f||h)&&!d.has(g))for(c.push(g),d.add(g),f=g.Vw,h=0;h<f.length;h++)b(g,f[h])}var c=[],d=new Set;gvjs_Re(a,gvjs_4Y);for(var e=0;e<a.length;e++)b(null,a[e]);return c};var gvjs_5Y={start:0,center:.5,end:1};function gvjs_6Y(a,b,c,d){if(null==a)throw Error(gvjs_ls);this.Z=a;this.Xe=(new gvjs_VY).Ac(a);this.m=b;this.eb=d;this.Ww=c;this.cH=new gvjs_YY(b);this.PB=0}
gvjs_6Y.prototype.$g=function(){for(var a=this.Z,b=a.ca(),c=[],d=0;d<b;++d)c.push(gvjs_dla(this,a,d));b=gvjs_ela(c);a=gvjs_L(this.m,"gantt.defaultStartDate",Date.now());a=new Date(a);gvjs_K(this.m,"gantt.sortTasks",!0)?a=b.sort(a):(b=gvjs_0Y(b),d=gvjs_1Y(b),gvjs_2Y(d,a),gvjs_3Y(d),a=b);b=a;d=gvjs_oy(this.m,"gantt.labelStyle");var e=gvjs_L(this.m,"gantt.labelMargin",16),f=gvjs_fla(this,b,d,e),g=gvjs_gla(b);a=new gvjs_ZS(this.eb.width-f,g.min,g.max,f,0,0);var h=g.max;if(gvjs_K(this.m,"gantt.criticalPathEnabled",
!0))for(g=[],gvjs_7Y(g,b,h);0<g.length;)h=g.shift(),gvjs_7Y(g,h.NA,h.Xd);var k=gvjs_L(this.m,"gantt.barHeight",d.fontSize+12),l=gvjs_L(this.m,"gantt.trackHeight",k+16);g={rect:new gvjs_5(0,0,this.eb.width,this.eb.height),options:gvjs_8Y(this.m,gvjs_et)};gvjs_sx===gvjs_J(this.m,gvjs_UY,gvjs_st)?this.PB=l:this.PB=0;h=this.Z.ca();for(var m=this.eb.width,n=[],p=[],q=gvjs_9Y(gvjs_8Y(this.m,"gantt.innerGridTrack"),gvjs_lp,gvjs_ly(this.m,gvjs_ft,gvjs_ea)),r=gvjs_9Y(gvjs_8Y(this.m,"gantt.innerGridDarkTrack"),
gvjs_lp,gvjs_tj(gvjs_Zz(gvjs_uj(q.fill),.04))),t=gvjs_9Y(gvjs_8Y(this.m,"gantt.innerGridHorizLine"),gvjs_Zp,gvjs_tj(gvjs_Zz(gvjs_uj(q.fill),.12))),u=0;u<h;++u)p.push({rect:new gvjs_5(0,u*l+this.PB,m,l),options:u%2?r:q});for(q=1;q<h;++q)n.push({line:new gvjs_9z(0,q*l,m,q*l),options:t});p.push({rect:new gvjs_5(0,this.PB,this.eb.width,h*l),options:t});gvjs_sx===gvjs_J(this.m,gvjs_UY,gvjs_st)?a.xp=-13.5:a.xp=h*l;h={lines:n,zS:p};k=gvjs_hla(this,b,a,l,k);l=gvjs_ila(this,b);m=[];p=gvjs_K(this.m,"gantt.shadowEnabled",
!0);n=gvjs_L(this.m,"gantt.shadowOffset");if(p&&0!=n)for(t=gvjs_L(this.m,gvjs_TY),p=gvjs_8Y(this.m,"gantt.shadowStyle"),0<t&&(p=Object.create(p),p[gvjs_8o]=t,p[gvjs_9o]=t),t=0;t<b.length;t++)q=b[t],0<q.Vw.length&&(r=q.zn,m.push({idx:q.yi,rect:new gvjs_5(r.left,r.top+n+this.PB,r.width,r.height),options:p}));d=gvjs_jla(this,b,d,e,f);b=gvjs_kla(this,b);e=[];a.draw(gvjs_s(this.Yoa,this),gvjs_s(this.dma,this,e),gvjs_ze);return{Fka:e,background:g,grid:h,Vua:l,Rwa:m,size:this.eb,Nxa:b,Oxa:d,Pxa:k,A8:this.cH,
xga:c,rY:a.PC}};function gvjs_hla(a,b,c,d,e){var f=gvjs_L(a.m,gvjs_TY),g=[];gvjs_u(b,function(h,k){k=k*d+(d-e)/2+this.PB;var l=c.scale(h.Xd.getTime()),m=c.scale(h.yf.getTime());var n=this.cH;var p=h.Xea;if(!n.qa.has(p)){var q=n.qa,r=q.set;n.A1>=n.oh.length&&(n.A1=0);var t=n.A1++;r.call(q,p,t)}n=n.qa.get(p);h.UB=n;n=this.cH.color(n);k=new gvjs_5(l,k,m-l,e);h.zn=k;g.push({idx:h.yi,rect:new gvjs_5(k.left,k.top,k.width,k.height),options:{"corners.rx":f,"corners.ry":f,fill:n}})},a);return g}
function gvjs_ila(a,b){var c=[];if(gvjs_K(a.m,"gantt.percentEnabled",!0)){var d=gvjs_L(a.m,gvjs_TY),e=Object.create(gvjs_8Y(a.m,"gantt.percentStyle"));e[gvjs_$o]=d;e[gvjs_ap]=d;e[gvjs_bp]=0;e[gvjs_cp]=0;e[gvjs_4o]=d;e[gvjs_5o]=d;e[gvjs_6o]=0;e[gvjs_7o]=0;gvjs_u(b,function(f){var g=f.yi,h=f.jea,k=this.cH.qb(f.UB);if(null!=h&&0<h){var l=Object.create(e);l.fill=k;h=Math.min(100,h)/100;f=f.zn;(1-h)*f.width<d&&(l[gvjs_bp]=l[gvjs_cp]=l[gvjs_6o]=l[gvjs_7o]=d);c.push({idx:g,rect:new gvjs_5(f.left,f.top,h*
f.width,f.height),options:l})}},a)}return c}function gvjs_fla(a,b,c,d){var e=gvjs_L(a.m,"gantt.labelMaxWidth",300);b=b.reduce(function(f,g){g=a.Ww(g.getName(),c).width+2*d;return Math.max(g,f)},0);return Math.min(e,b)}function gvjs_jla(a,b,c,d,e){var f=c.bb,g=c.fontSize,h=[];gvjs_u(b,function(k){var l=k.yi,m=k.zn,n=this.cH.color(k.UB);h.push({idx:l,anchor:new gvjs_z(e-d,m.top+m.height/2),text:k.getName(),options:{fontFamily:f,fontSize:g,fill:n,halign:1,valign:.5}})},a);return h}
function gvjs_kla(a,b){var c=gvjs_L(a.m,"gantt.arrow.spaceAfter"),d=gvjs_L(a.m,"gantt.arrow.length"),e=gvjs_L(a.m,"gantt.arrow.angle"),f=gvjs_J(a.m,"gantt.arrow.color"),g=gvjs_L(a.m,"gantt.arrow.width"),h=gvjs_L(a.m,"gantt.arrow.radius"),k=a.m.pb("gantt.criticalPathStyle"),l=[];gvjs_u(b,function(m){var n=m.yi,p=m.zn,q=p.left+p.width/2,r=p.top+p.height;gvjs_u(m.Vw,function(t){var u=t.yi,v=t.zn,w=v.left-c;v=v.top+v.height/2;var x={fill:gvjs_f,stroke:f,strokeWidth:g},y=!1;m.qH&&t.qH&&(y=!0,x.stroke=
k.stroke,x.strokeWidth=k.strokeWidth);l.push({fma:y,rect:new gvjs_5(q,r,w-q,v-r),lQ:n,WI:u,options:x})},this)},a);return{Bka:l,angle:e,length:d,radius:h}}
function gvjs_dla(a,b,c){var d=a.Xe;a=b.getValue(c,d.Bra.index());var e=b.getValue(c,d.qw.index()),f=b.getValue(c,d.vL.index()),g=b.getValue(c,d.WH.index()),h=b.getValue(c,d.pna.index()),k=b.getValue(c,d.Tua.index()),l=null!=d.Wea?b.getValue(c,d.Wea.index()):"";b=b.getValue(c,d.Nma.index())||"";b=gvjs_Fe(b.split(","),function(m,n){null!=n&&(n=gvjs_lf(n),0<n.length&&m.push(n));return m},[]);return new gvjs_ZY(c,a,e,f,g,h,k,b,l)}gvjs_6Y.prototype.Yoa=function(a,b){return this.Ww(a,b).width};
function gvjs_ela(a){var b=new gvjs__Y;gvjs_u(a,function(c){b.sB(c)});return b}function gvjs_7Y(a,b,c){gvjs_u(b,function(d){d.yf.getTime()>=c&&!d.qH&&(d.qH=!0,a.push(d))})}gvjs_6Y.prototype.dma=function(a,b,c,d,e,f,g,h){a.push({anchor:new gvjs_z(c,d),text:b,options:{fontFamily:h.bb,fontSize:h.fontSize,fontWeight:h.bold?gvjs_pt:gvjs_Yv,fill:h.color,halign:gvjs_5Y[f],valign:gvjs_5Y[g]}});return{}};function gvjs_9Y(a,b,c){if(null==a)a={yDa:c};else if(null==a[b]||a[b]==gvjs_f)a[b]=c;return a}
function gvjs_gla(a){return gvjs_Fe(a,function(b,c){if(null===b.max||b.max<c.yf.getTime())b.max=c.yf;if(null===b.min||b.min>c.Xd.getTime())b.min=c.Xd;return b},{max:null,min:null})}function gvjs_8Y(a,b){var c=void 0===c?{}:c;return a.pb(b,null,function(d){d=gvjs_x(d);var e=gvjs_Pj(d.fill||c.fill)||gvjs_f;d.fill=e;e=gvjs_Oj(d.fillOpacity);null!=e&&(d.fillOpacity=e);e=gvjs_Pj(d.stroke||c.stroke);null!=e&&(d.stroke=e);e=gvjs_Mj(d.strokeWidth);null!=e&&(d.strokeWidth=e);return d})||{}};function gvjs_$Y(a){gvjs_LR.call(this);this.ua=a;this.xa=this.CE=this.Ys=null;this.rz=1;this.F=null}gvjs_o(gvjs_$Y,gvjs_LR);gvjs_=gvjs_$Y.prototype;gvjs_.Tb=function(){return this.ua.size};gvjs_.cW=function(){var a=this.ua,b=[];gvjs_aZ(this,b,[a.background],null,gvjs_Uo);gvjs_aZ(this,b,a.grid.zS,null,gvjs_Mu);gvjs_lla(this,b,a.grid.lines);gvjs_bZ(this,b,this.ua.Fka,null,gvjs_Mu);return b};
gvjs_.AB=function(a){this.F=a.Oa().cp();var b=this.ua;a=[];var c=this.Ys?this.Ys.rb.ROW_INDEX:-1,d=this.Ys?this.Ys.rb.SOURCE:-1,e=-1;if(this.CE){var f=this.CE.rb.SUBTYPE;f&&0==f.indexOf("arrow")||(e=this.CE.rb.ROW_INDEX)}f=b.xga;var g=b.A8,h=gvjs_s(this.NW,this,[gvjs_s(this.KY,this,f,e,gvjs_s(g.jh,g)),gvjs_s(this.gka,this,f,c,d),gvjs_s(this.o$,this,f,c,d,gvjs_s(g.qb,g))]);gvjs_aZ(this,a,this.ua.Pxa,gvjs_ms,gvjs_zw,null,h);h=gvjs_s(this.NW,this,[gvjs_s(this.KY,this,f,e,gvjs_s(g.jh,g)),gvjs_s(this.o$,
this,f,c,d,function(k){k=g.qb(k);k=gvjs_uj(k);return gvjs_tj(gvjs_Zz(k,.25))})]);gvjs_aZ(this,a,this.ua.Vua,gvjs_ms,"rowoverlay",gvjs_vd,h);c=gvjs_s(this.NW,this,[gvjs_s(this.KY,this,f,e,function(){return gvjs_XY[gvjs_Pr]}),gvjs_s(this.X6,this,f,c,d)]);gvjs_aZ(this,a,this.ua.Rwa,gvjs_ms,"behindrows","shadows",c);gvjs_bZ(this,a,b.Oxa,gvjs_ms,gvjs_yw,"tasklabel");gvjs_mla(this,a,b.Nxa);this.xa&&(b=(new gvjs_oS([])).R(this.xa.layout,this.xa.offset),c=new gvjs_wR,gvjs_u(b,gvjs_s(c.add,c)),a.push(new gvjs_KR(c,
new gvjs_FL(gvjs_KQ),gvjs_Qd)));return a};gvjs_.NW=function(a,b,c){for(var d=a.length,e=0;e<d;++e)c=a[e].call(this,b,c)||c;return c};gvjs_.o$=function(a,b,c,d,e,f){var g=e.idx;a=a[g];if(b==g||c==g)f=f||Object.create(e.options),f.fill=d.call(this,a.UB);return f};gvjs_.KY=function(a,b,c,d,e){var f=d.idx;a=a[f];-1!=b&&b!=f&&(e=e||Object.create(d.options),e.fill=c.call(this,a.UB));return e};gvjs_.gka=function(a,b,c,d,e){return 0===a[d.idx].Vw.length?this.X6(a,b,c,d,e):null};
gvjs_.X6=function(a,b,c,d,e){a=d.idx;if(a==b||a==c)e=e||Object.create(d.options),e[gvjs_Vp]=0,e[gvjs_Wp]=2,e[gvjs_Up]=1,e[gvjs_Tp]=.2;return e};
function gvjs_mla(a,b,c){var d=c.angle,e=c.length,f=c.radius,g=e*Math.cos(d*Math.PI/180),h=e*Math.sin(d*Math.PI/180),k=a.Ys?a.Ys.rb.ROW_INDEX:-1,l=a.Ys?a.Ys.rb.SOURCE:-1,m=a.CE?a.CE.rb.ROW_INDEX:-1;gvjs_u(c.Bka,function(n){var p=null,q=!1,r=!1;if(0<=l)n.lQ==k&&n.WI==l&&(q=!0);else if(n.lQ==k||n.WI==k)q=!0;if(n.lQ==m||n.WI==m)r=!0;q&&(p=p||Object.create(n.options),p.strokeWidth=3);0<=m&&!r&&(p=p||Object.create(n.options),p.stroke=gvjs_XY[gvjs_Pr]);p=p||n.options;p=new gvjs_Sq(p);var t=n.rect;q=t.left;
r=t.top;var u=q+t.width,v=r+t.height;t=Math.min(t.width,t.height);t=Math.min(t,f);p.move(q,r).line(q,v-t).arc(q+t,v-t,t,t,180,90,!1).line(u,v).move(u-g,v-h).line(u+1,v).line(u-g,v+h);q=gvjs_GL(n.lQ,"arrow"+n.WI);gvjs_HL(q,gvjs_6a,n.WI);b.push(new gvjs_KR(p,q,n.fma?"linksoverlay":gvjs_QQ))},a)}function gvjs_cZ(a,b,c,d,e,f,g){gvjs_u(c,function(h){if(d){var k=new gvjs_FL(d);null!=h.idx&&gvjs_HL(k,gvjs_ns,h.idx)}else k=this.ay();g&&gvjs_HL(k,gvjs_ps,g);b.push(new gvjs_KR(f.call(this,h),k,e))},a)}
function gvjs_aZ(a,b,c,d,e,f,g){gvjs_cZ(a,b,c,d,e,function(h){var k=g&&g.call(this,h,null);k=k||h.options;h=h.rect;return new gvjs_1Q(h.left,h.top,h.width,h.height,k)},f)}function gvjs_lla(a,b,c){gvjs_cZ(a,b,c,null,gvjs_Mu,function(d){var e=d.line;return new gvjs_0Q(e.x0,e.y0,e.x1,e.y1,d.options)})}function gvjs_bZ(a,b,c,d,e,f){gvjs_cZ(a,b,c,d,e,function(g){var h=g.options;return new gvjs_ZQ(g.anchor.x,g.anchor.y,g.text,h)},f)}
gvjs_.ay=function(){var a=new gvjs_FL(gvjs_1r);gvjs_HL(a,gvjs_ps,"__internal_"+this.rz);this.rz+=1;return a};
gvjs_.bz=function(a,b){if(!b)this.xa=null;else if(!this.xa){a=this.ua.xga[Number(a.rb.ROW_INDEX)];var c=gvjs_4S(gvjs_7S(this.ua.rY));b=[];var d=c.tv(a.Xd,a.yf);b.push({title:"Duration:",subtitle:null,value:d,color:gvjs_XY[gvjs_Rr]});b.push({title:"Percent done:",subtitle:null,value:""+a.jea+" %",color:gvjs_XY[gvjs_Rr]});d=a.Xea;null!=d&&0<d.length&&b.push({title:"Resource:",subtitle:null,value:d,color:this.ua.A8.color(a.UB)});a.qH&&b.push({title:"Is on critical path",subtitle:null,value:"",color:gvjs_XY[gvjs_Rr]});
c=c.format(a.Xd,a.yf);c=a.getName()+": "+c;d=this.F.me;b=(new gvjs_fS).define(c,b).layout(d,{});c=this.Tb();c=new gvjs_5(0,0,c.width,c.height);a=(new gvjs_jS(c,a.zn,new gvjs_A(b.width(),b.height()),new gvjs_z(1,0))).position();this.xa={layout:b,offset:new gvjs_z(gvjs_1g(a.x,c.left,c.left+c.width-b.width()),gvjs_1g(a.y,c.top,c.top+c.height-b.height()))}}};gvjs_.nm=function(a,b,c){b.type==gvjs_uu?this.Ys=c?a:null:b.type==gvjs_k?this.CE=c?a:null:b.type==gvjs_Qd&&this.bz(a,c)};function gvjs_dZ(a){gvjs_RL.call(this,a)}gvjs_o(gvjs_dZ,gvjs_RL);gvjs_=gvjs_dZ.prototype;gvjs_.xq=function(){return{ROW_INDEX:gvjs_Dd}};
gvjs_.og=function(){return{backgroundColor:{fill:gvjs_ea},gantt:{arrow:{angle:45,color:gvjs_XY[gvjs_Tr],length:8,radius:30,spaceAfter:8,width:1.4},barCornerRadius:5,barHeight:null,criticalPathEnabled:!0,criticalPathStyle:{stroke:gvjs_QF[gvjs_Qr],strokeWidth:1.4},defaultStartDate:null,innerGridHorizLine:{stroke:null,strokeWidth:1},innerGridTrack:{fill:null},innerGridDarkTrack:{fill:null},labelMaxWidth:300,labelStyle:{fontName:gvjs_os,fontSize:14,color:gvjs_XY[gvjs_Rr]},percentEnabled:!0,percentStyle:{fill:gvjs_ca},
shadowEnabled:!0,shadowStyle:{fill:gvjs_XY[gvjs_Tr]},shadowOffset:1,trackHeight:null}}};gvjs_.Al=function(a,b,c,d){return new gvjs_6Y(a,b,c,d)};gvjs_.xs=function(){return[new gvjs_GR([new gvjs_FL(gvjs_ms)]),new gvjs_IR([new gvjs_FL(gvjs_ms)]),new gvjs_JR([new gvjs_FL(gvjs_ms)])]};gvjs_.Mm=function(a,b){return new gvjs_$Y(a,b)};gvjs_.po=function(a,b,c,d){a=new gvjs_xR(this,a,b,c,d);a.$t([gvjs_Uo,gvjs_Mu,gvjs_QQ,"linksoverlay","behindrows",gvjs_zw,"rowoverlay",gvjs_yw,gvjs_Qd]);return a};
gvjs_.nH=function(a,b){null==this.sb?this.sb=new gvjs_lR(this.container,a,b,[gvjs_os,gvjs_IQ]):this.sb.update(a,b)};gvjs_q(gvjs_mc,gvjs_dZ,void 0);gvjs_dZ.prototype.draw=gvjs_dZ.prototype.draw;gvjs_dZ.prototype.setSelection=gvjs_dZ.prototype.setSelection;gvjs_dZ.prototype.getSelection=gvjs_dZ.prototype.getSelection;gvjs_dZ.prototype.clearChart=gvjs_dZ.prototype.Jb;
