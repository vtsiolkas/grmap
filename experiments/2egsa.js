function wgs2egsa(lat, lng, z){
    lat=lat*Math.PI/180;
    lng=lng*Math.PI/180;
    var a = 6378137;
    var b = 6356752.31424518;
    var e2=(a*a-b*b)/(a*a);

    var N=a/Math.sqrt(1-e2*(Math.sin(lat)*Math.sin(lat)));
    var X=(N+z)*Math.cos(lat)*Math.cos(lng);
    var Y=(N+z)*Math.cos(lat)*Math.sin(lng);
    var Z=(N*(1-e2)+z)*Math.sin(lat);
    var px=199.723;
    var py=-74.03;
    var pz=-246.018;
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
    b = 6356752.31414036;
    lng=Math.atan2(Y1,X1);
    var lat0=Math.atan2(Z1,Math.sqrt(X1*X1+Y1*Y1));
    e2=(a*a-b*b)/(a*a);
    while(Math.abs(lat-lat0)>0.0000000001) {
        var N=a/Math.sqrt(1-e2*Math.sin(lat0)*Math.sin(lat0));
        var h=Math.sqrt(X1*X1+Y1*Y1)/Math.cos(lat0)-N;
        lat=lat0;
        lat0=Math.atan(Z1/Math.sqrt(X1*X1+Y1*Y1)*(1 / (1-e2*N/(N+h))));
    }
    lng = lng - 24*Math.PI/180;
    var m0 = 0.9996;
    var es2=(a*a-b*b)/(b*b);
    var V=Math.sqrt(1+es2*Math.cos(lat)*Math.cos(lat));
    var eta=Math.sqrt(es2*Math.cos(lat)*Math.cos(lat));
    var Bf=Math.atan(Math.tan(lat)/Math.cos(V*lng)*(1+eta*eta/6*(1-3*Math.sin(lat)*Math.sin(lat))*lng*lng*lng*lng));
    var Vf=Math.sqrt(1+es2*Math.cos(Bf)*Math.cos(Bf));
    var etaf=Math.sqrt(es2*Math.cos(Bf)*Math.cos(Bf));
    var n=(a-b)/(a+b);
    var r1=(1+n*n/4+n*n*n*n/64)*Bf;
    var r2=3/2*n*(1-n*n/8)*Math.sin(2*Bf);
    var r3=15/16*n*n*(1-n*n/4)*Math.sin(4*Bf);
    var r4=35/48*n*n*n*Math.sin(6*Bf);
    var r5=315/512*n*n*n*n*Math.sin(8*Bf);
    var Northing = a/(1+n)*(r1-r2+r3-r4+r5)*m0-0.001;
    var ys=Math.tan(lng)*Math.cos(Bf)/Vf*(1+etaf*etaf*lng*lng*Math.cos(Bf)*Math.cos(Bf)*(etaf*etaf/6+lng*lng/10)); ys = Math.log(ys + Math.sqrt(ys*ys+1));
    var Easting=m0*a*a/b*ys+500000;
    console.log(Easting, Northing)
}

wgs2egsa(43.34239169709919, 22.27463013948599, 0)