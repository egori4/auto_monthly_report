var gvjs_9S="border: 0; padding: 0; margin: 0;";gvjs_9H.prototype.OE=gvjs_V(67,function(a){this.ticks=a});gvjs_ZI.prototype.OE=gvjs_V(66,function(a){gvjs_9H.prototype.OE.call(this,a);var b=0;gvjs_u(this.ticks,function(c){c=this.Xq(c);b=Math.max(b,gvjs_mA(c/this.jfa))},this);this.n9=b});
function gvjs_$S(a,b,c,d,e){gvjs_H.call(this);this.ma=a;this.ga=b;this.Pa=c;this.Lga=new gvjs_iy({bb:gvjs_ct,fontSize:d,color:gvjs_kr,opacity:1,Lb:"",bold:!1,Nc:!1,Ue:!1});this.$ya=new gvjs_iy({bb:gvjs_ct,fontSize:d,color:gvjs_ot,opacity:1,Lb:"",bold:!1,Nc:!1,Ue:!1});this.Yxa=new gvjs_iy({bb:gvjs_ct,fontSize:0,color:gvjs_kr,opacity:1,Lb:"",bold:!1,Nc:!1,Ue:!1});this.vva=e;this.Um=this.ab=this.F=null;this.O2=[]}gvjs_o(gvjs_$S,gvjs_H);gvjs_=gvjs_$S.prototype;gvjs_.lf=function(){return this.Xa};
gvjs_.Ow=function(a){this.Xa=a};gvjs_.kf=function(){return this.Cb};gvjs_.bu=function(a){this.Cb=a};gvjs_.Wa=function(a,b,c){this.$d=a;this.WY=b;this.ku();a=gvjs_aT(this,a);null!=this.ZJ&&c?(this.Tf=new gvjs_ZE([this.ZJ],[a],c.duration,c.easing),gvjs_G(this.Tf,["begin","animate",gvjs_R],this.hua,!1,this),gvjs_G(this.Tf,gvjs_R,this.gua,!1,this),this.Tf.play(!1)):(this.ZJ=a,gvjs_bT(this))};gvjs_.OE=function(a,b){this.yca=Math.max(1,a);this.PD=Math.max(1,b)};gvjs_.T3=function(a){this.Iz=a};
function gvjs_cT(a,b,c,d){a.O2.push({hf:b,ol:c,color:d})}gvjs_.setAnimation=function(){};gvjs_.clear=function(){this.ku();gvjs_E(this.ab);this.ab=null;gvjs_li(this)};gvjs_.draw=function(a,b){var c=new gvjs_A(this.ga,this.Pa);null==this.ab?this.ab=new gvjs_0B(this.ma,c,a,b):this.ab.update(c,a);this.ab.rl(gvjs_s(this.no,this),a)};
gvjs_.no=function(){var a=this.ab.Oa(),b=a.Lm(this.ga,this.Pa);a.ic(b,gvjs_0t,gvjs_Iz);this.F=a;var c=this.Um=a.Sa(!1);a.appendChild(b,c);b=Math.round(.45*Math.min(this.ga,this.Pa));var d=this.ga/2,e=this.Pa/2;a.Ke(d-.5,e-.5,b,gvjs_dT,c);b-=gvjs_dT.strokeWidth;b=Math.round(.9*b);a.Ke(d-.5,e-.5,b,gvjs_eT,c);b-=2*gvjs_eT.strokeWidth;var f=.75*b;for(var g=0;g<this.O2.length;g++){var h=this.O2[g],k=gvjs_fT(this,gvjs_aT(this,h.hf)),l=gvjs_fT(this,gvjs_aT(this,h.ol)),m=new gvjs_PA,n=d+gvjs_5y(k,b),p=e+
gvjs_6y(k,b);m.move(n,p);m.Sf(d,e,b,b,k+90,l+90,!0);n=d+gvjs_5y(l,f);p=e+gvjs_6y(l,f);m.va(n,p);m.Sf(d,e,f,f,l+90,k+90,!1);m.close();a.Ia(m,new gvjs_3({fill:h.color}),c)}if(this.QL||this.m5)this.QL&&(f=e-Math.round(.35*b),a.Zi(this.QL,0,f,this.ga,f,gvjs_0,gvjs_0,this.Lga,c)),this.m5&&(f=e+Math.round(.35*b),a.Zi(this.m5,0,f,this.ga,f,gvjs_0,gvjs_0,this.Lga,c));h=this.PD;k=.8*b;l=.9*b;n=this.yca*h;p=(this.Cb-this.Xa)/n;var q=new gvjs_PA,r=new gvjs_PA,t=this.Yxa,u=Math.round(.14*b);t.fontSize=u;for(g=
0;g<=n;g++){var v=gvjs_fT(this,gvjs_aT(this,g*p+this.Xa)),w=0==g%h,x=w?k:l;m=w?q:r;var y=d+gvjs_5y(v,x);f=e+gvjs_6y(v,x);m.move(y,f);y=d+gvjs_5y(v,b);f=e+gvjs_6y(v,b);m.va(y,f);w&&this.Iz&&(m=this.Iz[Math.floor(g/h)])&&(y=d+gvjs_5y(v,x-u/2),f=e+gvjs_6y(v,x-u/2),x=gvjs_0,280<v||90>v?(x=gvjs_R,v=0):90<=v&&260>v?(x=gvjs_2,v=y,y=this.ga):(w=Math.min(y,this.ga-y),v=y-w,y+=w,f+=Math.round(u/4)),a.Zi(m,v,f,y,f,x,gvjs_0,t,c))}a.Ia(r,gvjs_8ia,c);a.Ia(q,gvjs_9ia,c);this.ku();this.qda=b;gvjs_bT(this);this.vva()};
gvjs_.hua=function(a){this.ZJ=a.x;gvjs_bT(this)};gvjs_.gua=function(){this.ku()};gvjs_.ku=function(){this.Tf&&(gvjs_li(this.Tf),this.Tf.stop(!1),gvjs_E(this.Tf),this.Tf=null)};function gvjs_aT(a,b){a=(b-a.Xa)/(a.Cb-a.Xa);a=Math.max(a,-.02);return a=Math.min(a,1.02)}function gvjs_fT(a,b){return a.l7*b+gvjs_2y((360-a.l7)/2+90)}
function gvjs_bT(a){if(a.F){var b=a.qda,c=a.F,d=a.ga/2,e=a.Pa/2,f=gvjs_fT(a,a.ZJ),g=Math.round(.95*b),h=Math.round(.3*b),k=gvjs_5y(f,g);g=gvjs_6y(f,g);var l=gvjs_5y(f,h);h=gvjs_6y(f,h);f=gvjs_2y(f+90);var m=.07*b,n=gvjs_5y(f,m);m=gvjs_6y(f,m);f=new gvjs_PA;f.move(d+k,e+g);f.Jp(d+n,e+m,d-l+n/2,e-h+m/2,d-l,e-h);f.Jp(d-l-n/2,e-h-m/2,d-n,e-m,d+k,e+g);k=Math.round(.15*b);(g=a.pda)?c.qc(g):g=a.pda=c.Sa();a.WY&&(b=e+Math.round(.75*b),c.Zi(a.WY,0,b,a.ga,b,gvjs_0,gvjs_0,a.$ya,g));c.Ia(f,gvjs_$ia,g);c.Ke(d-
.5,e-.5,k,gvjs_aja,g);c.appendChild(a.Um,g)}}var gvjs_dT=new gvjs_3({fill:gvjs_wr,stroke:gvjs_kr,strokeWidth:1}),gvjs_eT=new gvjs_3({fill:"#f7f7f7",stroke:gvjs_xr,strokeWidth:2}),gvjs_8ia=new gvjs_3({stroke:gvjs_mr,strokeWidth:1}),gvjs_9ia=new gvjs_3({stroke:gvjs_kr,strokeWidth:2}),gvjs_$ia=new gvjs_3({fill:"#dc3912",fillOpacity:.7,stroke:"#c63310",strokeWidth:1}),gvjs_aja=new gvjs_3({fill:"#4684ee",stroke:gvjs_mr,strokeWidth:1});gvjs_=gvjs_$S.prototype;gvjs_.Xa=NaN;gvjs_.Cb=NaN;gvjs_.yca=NaN;
gvjs_.PD=NaN;gvjs_.$d=0;gvjs_.WY=null;gvjs_.QL=null;gvjs_.m5=null;gvjs_.l7=270;gvjs_.qda=0;gvjs_.pda=null;gvjs_.ZJ=null;gvjs_.Iz=null;gvjs_.Tf=null;function gvjs_gT(a,b,c,d){this.ma=a;this.ga=b;this.Pa=c;this.cP=d;this.Ky=[];this.mc=[];this.Iz=[];this.XY=[];this.Kq=[];this.Xa=0;this.Cb=100;this.m7=this.T2=this.BS=this.AS=this.o6=this.gV=this.fV=this.OZ=this.JP=this.IP=null;this.vr=!0;this.M1=0}gvjs_=gvjs_gT.prototype;gvjs_.Ow=function(a){this.Xa!=a&&(this.Xa=a,this.vr=!0)};gvjs_.lf=function(){return this.Xa};gvjs_.bu=function(a){this.Cb!=a&&(this.Cb=a,this.vr=!0)};gvjs_.kf=function(){return this.Cb};gvjs_.setAnimation=function(a){this.m7=a};
gvjs_.setValues=function(a,b,c){this.vr=this.vr||this.mc.length!=a.length||this.Kq.length!=c.length||!gvjs_Gy(this.Kq,c);this.mc=a;this.XY=b;this.Kq=c};gvjs_.T3=function(a){1==a.length&&(a=["",a[0],""]);gvjs_Gy(this.Iz,a)||(this.Iz=a,this.vr=!0)};function gvjs_hT(a,b,c){return Math.min(Math.floor(a.ga/c),Math.floor(a.Pa/b))}gvjs_.draw=function(a){if(this.vr)gvjs_bja(this,a);else for(a=0;a<this.mc.length;a++){var b=this.Ky[a];b.QL=this.Kq[a];b.Wa(this.mc[a],this.XY[a],this.m7)}};
function gvjs_bja(a,b){a.clear();var c=a.mc.length,d=1,e=1;if(1<c){var f=Math.floor(Math.sqrt(a.ga*a.Pa/c));e=Math.floor(a.ga/f);for(d=Math.floor(a.Pa/f);!(c<=Math.floor(a.ga/f)*Math.floor(a.Pa/f));){var g=gvjs_hT(a,d,e+1),h=gvjs_hT(a,d+1,e);g>=h&&(f=g,e++);h>=g&&(f=h,d++)}}f=gvjs_hT(a,d,e);f-=0;h=gvjs_Oh();h.qc(a.ma);a.Ky=[];if(0!=c){var k=h.J(gvjs_os,{style:gvjs_9S,cellpadding:0,cellspacing:0,align:gvjs_0}),l=h.J(gvjs_ps,null);h.appendChild(k,l);g=[];for(var m=0,n=0;n<d;n++){var p=h.J(gvjs_rs,{style:gvjs_9S});
h.appendChild(l,p);for(var q=0;q<e;q++){var r=h.J(gvjs_qs,{style:"border: 0; padding: 0; margin: 0; width: "+f+"px;"});g[m++]=r;h.appendChild(p,r)}}h.appendChild(a.ma,k);d=Math.round(.1*f);a.M1=0;a.vr=!0;for(e=0;e<c;e++)h=a.Ky[e]=new gvjs_$S(g[e],f,f,d,gvjs_s(function(){this.M1++;this.M1==this.Ky.length&&(this.vr=!1)},a)),h.Ow(a.Xa),h.bu(a.Cb),h.QL=a.Kq[e],k=a.Iz,l=k.length,h.OE(1<l?l-1:4,a.PD),0<l&&h.T3(k),h.Wa(a.mc[e],a.XY[e],null),null!=a.IP&&null!=a.JP&&gvjs_cT(h,a.IP,a.JP,a.OZ),null!=a.fV&&null!=
a.gV&&gvjs_cT(h,a.fV,a.gV,a.o6),null!=a.AS&&null!=a.BS&&gvjs_cT(h,a.AS,a.BS,a.T2),h.draw(b,a.cP)}}gvjs_.clear=function(){for(var a=0;a<this.Ky.length;++a)this.Ky[a].clear();this.Ky=[]};gvjs_.PD=2;function gvjs_iT(a){gvjs_Nn.call(this,a)}gvjs_o(gvjs_iT,gvjs_Nn);gvjs_=gvjs_iT.prototype;
gvjs_.Rd=function(a,b,c){var d=new gvjs_yj([c||{}]);c=this.container;var e=this.La(d),f=this.getHeight(d),g=gvjs_K(d,gvjs_Bu);if(e!=this.ga||f!=this.Pa||g!=this.cP)this.xL&&this.xL.clear(),this.xL=new gvjs_gT(c,e,f,g),this.ga=e,this.Pa=f,this.cP=g;c=this.xL;e=gvjs_L(d,gvjs_Lv,0);c.Ow(e);e=gvjs_L(d,gvjs_Dv,100);c.bu(e);e=d.fa("majorTicks",[String(c.lf()),"","","",String(c.kf())]);c.T3(e);e=gvjs_L(d,"minorTicks",2);c.PD!=e&&(c.PD=e,c.vr=!0);e=d.Aa("greenFrom");f=d.Aa("greenTo");g=d.Aa("yellowFrom");
var h=d.Aa("yellowTo"),k=d.Aa("redFrom"),l=d.Aa("redTo"),m=gvjs_ly(d,"greenColor",gvjs_ir),n=gvjs_ly(d,"yellowColor",gvjs_tr),p=gvjs_ly(d,"redColor",gvjs_sr);if(c.IP!=e||c.JP!=f||c.OZ!=m||c.fV!=g||c.gV!=h||c.o6!=n||c.AS!=k||c.BS!=l||c.T2!=p)c.IP=e,c.JP=f,c.OZ=m,c.fV=g,c.gV=h,c.o6=n,c.AS=k,c.BS=l,c.T2=p,c.vr=!0;d=gvjs_2K(d,400,gvjs_$u);c.setAnimation(d);d=[];e=[];f=[];if(2==b.$()&&b.W(0)==gvjs_l&&b.W(1)==gvjs_g)for(g=0;g<b.ca();g++)null!=b.getValue(g,0)&&null!=b.getValue(g,1)&&(f.push(b.getValue(g,
0)),d.push(b.getValue(g,1)),e.push(b.Ha(g,1)));else for(h=0;h<b.$();h++)if(b.W(h)==gvjs_g)for(g=0;g<b.ca();g++)null!=b.getValue(g,h)&&(d.push(b.getValue(g,h)),e.push(b.Ha(g,h)),f.push(b.Ga(h)));c.setValues(d,e,f);c.draw(a);gvjs_I(this,gvjs_i,null)};gvjs_.He=function(){this.xL&&this.xL.clear()};gvjs_.ga=0;gvjs_.Pa=0;gvjs_.cP=!0;gvjs_q(gvjs_mc,gvjs_iT,void 0);gvjs_iT.prototype.draw=gvjs_iT.prototype.draw;gvjs_iT.prototype.clearChart=gvjs_iT.prototype.Jb;gvjs_iT.prototype.getContainer=gvjs_iT.prototype.getContainer;