var gvjs_Y3="linktable",gvjs_Z3="sankey.link.color.focused",gvjs_upa="sankey.link.color.selected",gvjs_vpa="sankey.link.color.unfocused",gvjs_wpa="sankey.link.color.unselected",gvjs__3="sankey.node.color.focused",gvjs_xpa="sankey.node.color.selected",gvjs_ypa="sankey.node.color.unfocused",gvjs_zpa="sankey.node.color.unselected",gvjs_03="sankey.node.label.focused",gvjs_Apa="sankey.node.label.selected",gvjs_Bpa="sankey.node.label.unfocused",gvjs_Cpa="sankey.node.label.unselected",gvjs_13="unique";
function gvjs_23(){}gvjs_o(gvjs_23,gvjs_zl);gvjs_23.prototype.Pb=function(a){try{this.Ac(a)}catch(b){return!1}return!0};
gvjs_23.prototype.Ac=function(a){if(Array.isArray(a)){var b=a;a=gvjs_Al(b[0]);b=gvjs_Al(b[1]);var c=a.$();if(3>c)throw Error("Invalid linkTable format: must have at least 3 columns.");this.jb(gvjs_Y3,a,0,gvjs_g);this.jb(gvjs_Y3,a,1,gvjs_g);this.jb(gvjs_Y3,a,2,gvjs_g);var d=null,e=null,f=null,g=3;3<c&&""==a.Jg(3)&&(this.jb(gvjs_Y3,a,3,gvjs_g),d=3,g=4);for(c=g;c<a.$();++c)g=a.Jg(c),g==gvjs_Jd&&null===e?(e=c,this.jb(gvjs_Y3,a,c,gvjs_l)):g==gvjs_Pd&&null===f&&(f=c,this.jb(gvjs_Y3,a,c,gvjs_l));c=b.$();
if(1!==c&&2!==c)throw Error("Invalid nodeTable format: must have 1 or 2 columns.");this.jb("nodetable",b,0,gvjs_l);2===c&&this.jb("nodetable",b,1,gvjs_l);g=[];for(var h=[],k=b.ca(),l=0,m=a.ca();l<m;++l){var n=a.getValue(l,0),p=a.getValue(l,1);if(n>=k||p>=k)throw Error("Invalid linkTable row: source and target nodes must be in the range 0 to "+(k-1)+".");var q=a.getValue(l,2),r=null,t=null,u=null;null!=e&&(r=a.getStringValue(l,e));null!=d&&(t=a.getValue(l,d));null!=f&&(u=a.getValue(l,f));h.push({source:n,
target:p,value:q,style:r,tooltip:u,opacity:t})}a=0;for(e=b.ca();a<e;++a)g.push({name:b.getValue(a,0),Eb:2===c?b.getValue(a,1):""});return{links:h,nodes:g,pF:f,YR:d}}a=gvjs_Al(a);c=a.$();if(3>c)throw Error("Invalid data table format: must have at least 3 columns.");this.jb(gvjs_cp,a,0,gvjs_l);this.jb(gvjs_cp,a,1,gvjs_l);this.jb(gvjs_cp,a,2,gvjs_g);f=d=b=null;e=3;3<c&&""==a.Jg(3)&&(this.jb(gvjs_cp,a,3,gvjs_g),b=3,e=4);for(c=e;c<a.$();++c)e=a.Jg(c),e==gvjs_Jd&&null===d?(d=c,this.jb(gvjs_cp,a,c,gvjs_l)):
e==gvjs_Pd&&null===f&&(f=c,this.jb(gvjs_cp,a,c,gvjs_l));c=new Map;e=[];g=[];h=0;for(k=a.ca();h<k;++h)l=a.getStringValue(h,0),m=a.getStringValue(h,1),l=gvjs_Dpa(c,e,l),m=gvjs_Dpa(c,e,m),n=a.getValue(h,2),p=null,null!=d&&(p=a.getStringValue(h,d)),q=null!=f?a.getValue(h,f):null,r=null,null!=b&&(r=a.getValue(h,b)),g.push({source:l,target:m,value:n,style:p,tooltip:q,opacity:r});return{links:g,nodes:e,pF:f,YR:b}};
function gvjs_Dpa(a,b,c){if(a.has(c))return a.get(c);a.set(c,b.length);b.push({name:c,Eb:""});return b.length-1}gvjs_23.prototype.jb=function(a,b,c,d,e){if(!gvjs_Dl(b,c,d,e))throw Error(gvjs_fs+a+": column #"+c+gvjs_ba+d+"'.");};function gvjs_33(a,b){gvjs_LR.call(this);this.xa=null;this.Hi=b;this.VI=null;this.y3=new Set;this.x3=new Set;this.ua=a}gvjs_o(gvjs_33,gvjs_LR);
gvjs_33.prototype.AB=function(a){var b=[],c=gvjs_DL(a.Oa());this.xa&&(this.ua.$f?gvjs_FG(this.xa,this.Hi.getContainer()):b.push(new gvjs_KR(gvjs_HG(this.xa,c).j(),new gvjs_FL(gvjs_KQ),gvjs_Pd)),this.xa=null);var d=new Set,e=new Set,f=new Set,g=new Set;null!=this.VI&&gvjs_Epa(this,this.VI,e,d);var h=gvjs_8d(this.x3);for(a=h.next();!a.done;a=h.next())gvjs_Fpa(this,a.value,f,g);h=gvjs_8d(this.y3);for(a=h.next();!a.done;a=h.next())gvjs_Gpa(this,a.value,f,g);var k=0<g.size,l=0<d.size;gvjs_u(this.ua.labels,
function(p,q){var r=p.styles.Hd,t=gvjs_QQ;g.has(q)&&d.has(q)?(r=p.styles.dL,t=gvjs_zs):d.has(q)?r=p.styles.focused:g.has(q)?(r=p.styles.selected,t=gvjs_zs):k&&l?r=p.styles.eM:k?r=p.styles.dM:l&&(r=p.styles.cM);p=c.ys(p.text,p.x,p.y,p.width,p.angle,p.bA,p.dA,r);q=gvjs_HL(gvjs_HL(new gvjs_FL(gvjs_1r),gvjs_ls,q),gvjs_ns,gvjs_8c);b.push(new gvjs_KR(p,q,t))},this);gvjs_u(this.ua.zS,function(p,q){var r=gvjs_HL(gvjs_HL(gvjs_GL(q),gvjs_ns,"node"),"NAME",this.ua.labels[q].text),t=p.Rb.Hd,u=gvjs_QQ;g.has(q)&&
d.has(q)?(t=p.Rb.dL,u=gvjs_VQ):d.has(q)?t=p.Rb.focused:g.has(q)?(u=gvjs_VQ,t=p.Rb.selected):k&&l?t=p.Rb.eM:k?t=p.Rb.dM:l&&(t=p.Rb.cM);p=c.Bl(p.x,p.y,p.width,p.height,t);b.push(new gvjs_KR(p,r,u))},this);var m=0<f.size,n=0<e.size;gvjs_u(this.ua.paths,function(p,q){var r=gvjs_HL(gvjs_HL(new gvjs_FL(gvjs_ks),gvjs_ls,q),gvjs_ns,"link"),t=p.Rb.Hd,u=gvjs_zw;f.has(q)&&e.has(q)?(t=p.Rb.dL,u=gvjs_VQ):e.has(q)?t=p.Rb.focused:f.has(q)?(u=gvjs_VQ,t=p.Rb.selected):m&&n?t=p.Rb.eM:m?t=p.Rb.dM:n&&(t=p.Rb.cM);p=c.Dc(p.vc,
t);b.push(new gvjs_KR(p,r,u))},this);return b};gvjs_33.prototype.Tb=function(){return this.ua.size};function gvjs_Epa(a,b,c,d){b=b.rb.SUBTYPE;if(null!=a.VI){var e=a.VI.rb.ROW_INDEX;"node"===b?gvjs_Gpa(a,e,c,d):"link"===b&&gvjs_Fpa(a,e,c,d)}}function gvjs_Fpa(a,b,c,d){a=a.ua.paths[b];c.add(b);d.add(a.G$);d.add(a.Mga)}function gvjs_Gpa(a,b,c,d){d.add(b);gvjs_u(gvjs_lj(a.ua.Tsa[b]),function(e){c.add(e);e=a.ua.paths[e];d.add(e.G$);d.add(e.Mga)})}
gvjs_33.prototype.nm=function(a,b,c){switch(b.type){case gvjs_Pd:a.type()===gvjs_ks?this.bz(a,c):a.type();break;case gvjs_uu:a.type()===gvjs_ks?this.VI=c?a:null:a.type();break;case gvjs_k:a.type()===gvjs_ks&&(b=a.rb.ROW_INDEX,"node"===a.rb.SUBTYPE?c?this.y3.add(b):this.y3.delete(b):c?this.x3.add(b):this.x3.delete(b))}};
gvjs_33.prototype.bz=function(a,b){this.Hi.clear();this.xa=null;if(b){b=a.rb.SUBTYPE;var c=a.rb.ROW_INDEX;a=this.ua.size;a=new gvjs_B(0,a.width,a.height,0);var d=null,e=null,f=null,g=null;"node"==b?(g=this.ua.zS[c],e=new gvjs_z(g.x,g.y),f=gvjs_bz(e,new gvjs_z(-1,1))):"link"==b&&(g=this.ua.paths[c],b=g.vc,e=new gvjs_z((b.vc[0].data.x+b.vc[1].data.x)/2,(b.vc[0].data.y+b.vc[1].data.y)/2),f=gvjs_bz(e,new gvjs_z(-1,1)));g.tooltip&&e&&f&&(g.tooltip.content&&this.ua.$f?d={html:gvjs_5f(gvjs_Ob,{"class":gvjs_Ku},
gvjs_LA(g.tooltip.content)),kO:g.tooltip.Nh,pivot:f,anchor:e,HG:a,spacing:20,margin:5}:(b={entries:[]},g.tooltip.content?b.entries.push(gvjs_eG(g.tooltip.content,this.ua.Dp)):g.tooltip.title&&(b.entries.push(gvjs_eG(g.tooltip.title,this.ua.Dp)),b.entries.push(gvjs_eG(g.tooltip.rxa.toString(),this.ua.Dp,g.tooltip.pxa,this.ua.Dp)),g.tooltip.Rda&&g.tooltip.Sda&&b.entries.push(gvjs_eG(g.tooltip.Sda.toString(),this.ua.Dp,g.tooltip.Rda,this.ua.Dp))),d=gvjs_hG(b,this.ua.sc,!1,e,a,f,void 0,this.ua.$f)));
d&&(this.xa=d)}};var gvjs_Hpa={NONE:gvjs_f,wBa:"source",HBa:"target",lAa:gvjs_yp},gvjs_Ipa={rV:gvjs_Et,TBa:gvjs_13};function gvjs_Jpa(a,b,c,d){this.Z=a;this.m=b;this.Zd=c;this.eb=d;this.gb=(new gvjs_23).Ac(a);this.xsa=gvjs_L(b,"sankey.iterations");this.qca=gvjs_ny(b,"sankey.link.color");gvjs_ny(b,"sankey.link.focused");gvjs_ny(b,"sankey.link.unfocused");a=b.cD("sankey.link.colors");this.rca=null==a?null:gvjs_v(a,function(e){return gvjs_tj(gvjs_oj(e).hex)});this.uD=gvjs_J(b,"sankey.link.colorMode",gvjs_f,gvjs_Hpa);this.Gma=gvjs_L(b,"sankey.link.defaultOpacity",this.qca.fillOpacity);this.Yca=gvjs_L(b,"sankey.link.minOpacity",
.2);this.ita=gvjs_L(b,"sankey.link.maxOpacity",.6);a=b.cD("sankey.node.colors");this.Tta=null==a?null:gvjs_v(a,function(e){return gvjs_tj(gvjs_oj(e).hex)});this.Sta=gvjs_ny(b,"sankey.node.color");this.C1=gvjs_J(b,"sankey.node.colorMode",gvjs_13,gvjs_Ipa);this.eQ=gvjs_K(b,gvjs__u,!1);this.Oe=gvjs_oy(b,"sankey.node.label");this.bca=gvjs_L(b,"sankey.node.labelPadding");this.Uta=gvjs_L(b,"sankey.node.nodePadding");this.Vta=gvjs_L(b,"sankey.node.width")}
gvjs_Jpa.prototype.$g=function(){var a=gvjs_Kpa(this);gvjs_Lpa(a);var b=this.Oe.fontSize;b=d3.sankey().nodeWidth(this.Vta).nodePadding(this.Uta).size([this.eb.width,this.eb.height-b/2]).iterations(this.xsa);b(a);gvjs_Mpa(a.nodes);var c=new gvjs_XR(this.eQ,this.Tta),d=new gvjs_XR(this.eQ,this.rca),e=[],f=[],g=[],h=null==this.rca&&this.C1===gvjs_13;gvjs_u(a.nodes,function(w,x){w.idx=x;c.Au(this.C1===gvjs_Et?w.Eb:String(x));h||("source"===this.uD&&0<w.sourceLinks.length||"target"===this.uD&&0<w.targetLinks.length||
this.uD===gvjs_yp)&&d.Au(String(x))},this);var k=null;null!=this.gb.pF&&(k=this.gb.pF);var l=this.Z.Ga(2);null===l&&(l="Width");var m=null;null!=this.gb.YR&&(m=this.Z.Ga(this.gb.YR),null===m&&(m="Opacity"));var n=Infinity,p=-Infinity;null!=this.gb.YR&&gvjs_u(a.links,function(w){null!=w.opacity&&(n=Math.min(n,w.opacity),p=Math.max(p,w.opacity))},this);var q=c.cd(),r=h?q:d.cd();gvjs_u(a.links,function(w,x){w.idx=x;var y=this.Gma;null!=w.opacity&&p>n&&(y=this.Yca+(w.opacity-n)/(p-n)*(this.ita-this.Yca));
var z=this.qca.clone();z.mf(y);y="source"===this.uD?String(w.source.idx):"target"===this.uD?String(w.target.idx):null;null!=y?z.Te(r.Cq(y)):this.uD===gvjs_yp&&gvjs_$x(z,{Vf:r.Cq(String(w.source.idx)),sf:r.Cq(String(w.target.idx)),tn:1,un:1,x1:gvjs_Oo,y1:0,x2:gvjs_Po,y2:0,Sn:!0,sp:!1});y=w.style;if(null!=y&&(y=gvjs_9I(y),null!=y)){y=new gvjs_yj([y]);var A=void 0===A?"":A;z.Te(gvjs_ly(y,[A+gvjs_mp,A+gvjs_kp],z.fill));z.mf(gvjs_ky(y,A+gvjs_np,z.fillOpacity));z.rd(gvjs_ly(y,[A+gvjs_0p,A+gvjs_Yp],z.Uj()));
gvjs_8x(z,gvjs_ky(y,A+gvjs_1p,z.strokeOpacity));z.hl(gvjs_L(y,A+gvjs_2p,z.strokeWidth))}x=null!=k&&w.tooltip?{Nh:!(!this.Z.getProperty(x,k,gvjs_8u)&&!this.Z.Bd(k,gvjs_8u)),content:w.tooltip}:{title:w.source.name+" -> "+w.target.name,pxa:l,rxa:w.value,Rda:m,Sda:w.opacity};A=new gvjs_PA;y=w.source.x0+(w.source.x1-w.source.x0);var B=w.source.y0+(w.y0-w.source.y0-w.width/2),D=w.target.x0,C=w.target.y0+(w.y1-w.target.y0-w.width/2),G=(D-y)/3;A.move(y,B);A.Jp(y+G,B,y+2*G,C,D,C);A.va(D,C+w.width);A.Jp(y+
2*G,C+w.width,y+G,B+w.width,y,B+w.width);A.close();y=null==this.m.fa(gvjs_upa)?z.clone().mf(.8):gvjs_ny(this.m,gvjs_upa,z);B=null==this.m.fa(gvjs_Z3)?z.clone().mf(.8):gvjs_ny(this.m,gvjs_Z3,z);D=gvjs_ny(this.m,gvjs_vpa,z);C=null==this.m.fa(gvjs_wpa)?z.clone().mf(.2):gvjs_ny(this.m,gvjs_wpa,z);G=gvjs_ny(this.m,gvjs_Z3,y);var J=gvjs_ny(this.m,gvjs_vpa,C);e.push({Rb:{Hd:z,selected:y,focused:B,cM:D,dM:C,dL:G,eM:J},tooltip:x,G$:w.source.idx,Mga:w.target.idx,vc:A})},this);var t=this.eb.width,u=b.nodeWidth(),
v={};gvjs_u(a.nodes,function(w,x){var y=new Set;gvjs_u(w.sourceLinks,function(I){y.add(I.idx)},this);gvjs_u(w.targetLinks,function(I){y.add(I.idx)},this);v[x]=y;x=w.x0<t/2;var z=this.Sta.clone();z.Te(q.Cq(this.C1===gvjs_Et?w.Eb:String(w.idx)));z.rd(z.fill,0);var A=null==this.m.fa(gvjs_xpa)?z.clone().mf(1):gvjs_ny(this.m,gvjs_xpa,z),B=null==this.m.fa(gvjs__3)?z.clone().mf(1):gvjs_ny(this.m,gvjs__3,z),D=gvjs_ny(this.m,gvjs_ypa,z),C=null==this.m.fa(gvjs_zpa)?z.clone().mf(.2):gvjs_ny(this.m,gvjs_zpa,
z),G=gvjs_ny(this.m,gvjs__3,A),J=gvjs_ny(this.m,gvjs_ypa,C);g.push({Rb:{Hd:z,selected:A,focused:B,cM:D,dM:C,dL:G,eM:J},x:w.x0,y:w.y0,tooltip:w.tooltip,width:u,height:w.y1-w.y0});z=null==this.m.fa(gvjs_Apa)?gvjs_gy((new gvjs_iy(this.Oe)).setOpacity(.8),!0):gvjs_oy(this.m,gvjs_Apa,this.Oe);A=null==this.m.fa(gvjs_03)?gvjs_gy((new gvjs_iy(this.Oe)).setOpacity(.8),!0):gvjs_oy(this.m,gvjs_03,this.Oe);B=gvjs_oy(this.m,gvjs_Bpa,this.Oe);D=null==this.m.fa(gvjs_Cpa)?(new gvjs_iy(this.Oe)).setOpacity(.4):gvjs_oy(this.m,
gvjs_Cpa,this.Oe);C=gvjs_oy(this.m,gvjs_03,z);G=gvjs_oy(this.m,gvjs_Bpa,D);f.push({angle:0,bA:x?gvjs_2:gvjs_R,dA:gvjs_0,styles:{Hd:this.Oe,selected:z,focused:A,cM:B,dM:D,dL:C,eM:G},text:w.name,width:0,x:x?w.x0+u+this.bca:w.x0-this.bca,y:w.y0+(w.y1-w.y0)/2})},this);return{labels:f,paths:e,zS:g,Tsa:v,nodeWidth:u,size:this.eb,sc:this.Zd,$f:gvjs_K(this.m,gvjs_kx,!0),Dp:gvjs_oy(this.m,gvjs_mx)}};function gvjs_Kpa(a){a=a.gb;return{nodes:a.nodes,links:a.links}}
function gvjs_Lpa(a){var b=gvjs_v(a.nodes,function(e,f){return{index:f,Nga:[]}});gvjs_u(a.links,function(e){b[e.source].Nga.push(b[e.target])});a=new Set(b);for(var c=new Set,d=0;0<a.size;){if(d>b.length)throw a=gvjs_v(gvjs_lj(a),function(e){return e.index}).join(","),Error("Cycle found in rows: "+a);gvjs_u(gvjs_lj(a),function(e){gvjs_u(e.Nga,function(f){c.add(f)})});a=c;c=new Set;d++}}
function gvjs_Mpa(a){gvjs_u(a,function(b){gvjs_Qe(b.targetLinks,function(c,d){function e(f){return(f.target.y0-(f.source.y0+(f.y0-f.source.y0-f.width/2)))/(f.target.x0-f.source.x0)}return e(d)-e(c)})});gvjs_u(a,function(b){var c=0;gvjs_u(b.targetLinks,function(d){d.y1=c+d.target.y0+d.width/2;c+=d.width})})};function gvjs_43(a){gvjs_RL.call(this,a)}gvjs_o(gvjs_43,gvjs_RL);gvjs_=gvjs_43.prototype;gvjs_.xq=function(){return{NAME:gvjs_Wv}};
gvjs_.og=function(){return{backgroundColor:{fill:gvjs_Lx,stroke:gvjs_ot,strokeWidth:10,strokeOpacity:.2},tooltip:{isHtml:!1,textStyle:{fontName:gvjs__r,fontSize:16,color:gvjs_ot}},sankey:{iterations:32,link:{colorMode:gvjs_f,color:{fill:"#aaa",fillOpacity:.8,stroke:gvjs_f},defaultOpacity:.6,minOpacity:.2,maxOpacity:.6},node:{colorMode:gvjs_13,color:{fill:gvjs_ot,fillOpacity:.8},label:{fontName:gvjs_Aw,fontSize:10,color:gvjs_hr,bold:!1,italic:!1},labelPadding:6,nodePadding:10,width:10,interactivity:!1,
selectionMode:gvjs_Tw}}}};gvjs_.Mm=function(a,b){return new gvjs_33(a,b)};gvjs_.Al=function(a,b,c,d){return new gvjs_Jpa(a,b,c,d)};gvjs_.po=function(a,b,c,d){a=gvjs_RL.prototype.po.call(this,a,b,c,d);a.$t([gvjs_zw,gvjs_QQ,gvjs_yw,gvjs_VQ,gvjs_As,gvjs_zs,gvjs_Pd]);return a};
gvjs_.xs=function(a){var b=gvjs_K(a,"sankey.node.interactivity",!1),c=[new gvjs_GR([new gvjs_FL(gvjs_ks)]),new gvjs_JR([new gvjs_FL(gvjs_ks)])];b&&c.push(new gvjs_IR([gvjs_HL(new gvjs_FL(gvjs_ks),gvjs_ns,"node")]));gvjs_K(a,"sankey.link.interactivity",!1)&&(a=gvjs_J(a,"sankey.link.selectionMode",gvjs_Tw)===gvjs_Tw,c.push(new gvjs_HR([gvjs_HL(new gvjs_FL(gvjs_ks),gvjs_ns,"link")],a)));return c};gvjs_q(gvjs_Mc,gvjs_43,void 0);gvjs_43.prototype.draw=gvjs_43.prototype.draw;gvjs_43.prototype.setSelection=gvjs_43.prototype.setSelection;gvjs_43.prototype.getSelection=gvjs_43.prototype.getSelection;gvjs_43.prototype.clearChart=gvjs_43.prototype.Jb;gvjs_43.prototype.getContainer=gvjs_43.prototype.getContainer;
