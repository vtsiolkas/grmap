function egsa2wgs(X, Y, z){
    var a=6378137;
    var b=6356752.31414036;
    var m0=0.9996;
    var n=(a-b)/(a+b);
    var es2=(a*a-b*b)/(b*b);
    var B=(1+n)/a/(1+n*n/4+n*n*n*n/64)*Y/m0;
    var b1=3/2*n*(1-9/16*n*n)*Math.sin(2*B);
    var b2=n*n/16*(21-55/2*n*n)*Math.sin(4*B);
    var b3=151/96*n*n*n*Math.sin(6*B);
    var b4=1097/512*n*n*n*n*Math.sin(8*B);
    var Bf=B+b1+b2+b3+b4;
    var ID=Math.floor(X/1000000);
    var Vf=Math.sqrt(1+es2*Math.cos(Bf)*Math.cos(Bf));
    var etaf=Math.sqrt(es2*Math.cos(Bf)*Math.cos(Bf));
    var y=X-500000-ID*1000000;
    var ys=y*b/m0/(a*a);
    var l=Math.atan(Vf/Math.cos(Bf)*( (Math.exp(ys) - Math.exp(-ys))/2 )*(1-etaf*etaf*etaf*etaf*ys*ys/6-es2*ys*ys*ys*ys/10));
    var lng=24*Math.PI/180+l;
    var lat=Math.atan(Math.tan(Bf)*Math.cos(Vf*l)*(1-etaf*etaf/6*l*l*l*l));
    var e2=(a*a-b*b)/(a*a);
    var N=a/Math.sqrt(1-e2*(Math.sin(lat)*Math.sin(lat)));
    var X=(N+z)*Math.cos(lat)*Math.cos(lng);
    var Y=(N+z)*Math.cos(lat)*Math.sin(lng);
    var Z=(N*(1-e2)+z)*Math.sin(lat);
    var px=-199.723;
    var py=74.03;
    var pz=246.018;
    var rw=0;
    var rf=0;
    var rk=0;
    var ks=1;
    var c1 = Math.cos(rw);
    var c2 = Math.cos(rf);
    var c3 = Math.cos(rk);
    var s1 = Math.sin(rw);
    var s2 = Math.sin(rf);
    var s3 = Math.sin(rk);
    var D11 = c2*c3;
    var D21 = -c2*s3;
    var D31 = Math.sin(rf);
    var D12 = s1*s2*c3+c1*s3;
    var D22 = -s1*s2*s3+c1*c3;
    var D32 = -s1*c2;
    var D13 = -c1*s2*c3+s1*s3;
    var D23 = c1*s2*s3+s1*c3;
    var D33 = c1*c2;
    var X1 = px + ks*(D11*X+D12*Y+D13*Z);
    var Y1 = py + ks*(D21*X+D22*Y+D23*Z);
    var Z1 = pz + ks*(D31*X+D32*Y+D33*Z);
    b = 6356752.31424518; lng=Math.atan2(Y1,X1);
    var lat0=Math.atan2(Z1,Math.sqrt(X1*X1+Y1*Y1));
    e2=(a*a-b*b)/(a*a);
    while(Math.abs(lat-lat0)>0.0000000001) {
        var N=a/Math.sqrt(1-e2*Math.sin(lat0)*Math.sin(lat0));
        var h=Math.sqrt(X1*X1+Y1*Y1)/Math.cos(lat0)-N;
        lat=lat0;
        lat0=Math.atan(Z1/Math.sqrt(X1*X1+Y1*Y1)*(1 / (1-e2*N/(N+h))));
    }
    h=h-0.001;
    lat=lat*180/Math.PI;
    lng=lng*180/Math.PI;
    console.log(lat, lng)
}
egsa2wgs(360000,4800000, 0)