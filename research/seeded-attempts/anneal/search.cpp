// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Science Ladder contributors
// Independent random-start simulated annealing for aperiodic LABS512.
#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <string>

constexpr int N=512;
struct Random {
 uint64_t state;
 uint64_t next(){uint64_t z=(state+=0x9e3779b97f4a7c15ULL);z=(z^(z>>30))*0xbf58476d1ce4e5b9ULL;z=(z^(z>>27))*0x94d049bb133111ebULL;return z^(z>>31);}
 int index(){return next()&511;}
 double unit(){return (next()>>11)*0x1.0p-53;}
};
struct State {
 std::array<int,N> s{},c{};
 int energy=0;
 void recompute(){energy=0;c.fill(0);for(int k=1;k<N;k++){for(int i=0;i<N-k;i++)c[k]+=s[i]*s[i+k];energy+=c[k]*c[k];}}
 int delta(int p)const{int change=0;for(int k=1;k<N;k++){int v=0;if(p>=k)v+=s[p-k];if(p+k<N)v+=s[p+k];int d=-2*s[p]*v;change+=2*c[k]*d+d*d;}return change;}
 void flip(int p,int d){for(int k=1;k<N;k++){int v=0;if(p>=k)v+=s[p-k];if(p+k<N)v+=s[p+k];c[k]-=2*s[p]*v;}s[p]=-s[p];energy+=d;}
};
void save(const std::string&base,const State&best,uint64_t seed,uint64_t iterations,uint64_t cycle){
 std::ofstream sequence(base+".txt");for(int x:best.s)sequence<<(x>0?'+':'-');sequence<<'\n';
 std::ofstream meta(base+".json");meta<<"{\"seed\":\""<<seed<<"\",\"iterationsCompleted\":"<<iterations<<",\"cyclesCompleted\":"<<cycle<<",\"energy\":"<<best.energy<<",\"length\":512}\n";
}
int main(int argc,char**argv){
 if(argc!=4){std::cerr<<"usage: search SEED ITERATIONS OUTPUT_PREFIX\n";return 2;}
 const uint64_t seed=std::stoull(argv[1]),iterations=std::stoull(argv[2]);std::string base=argv[3];Random random{seed};State current,best;best.energy=INT32_MAX;
 constexpr uint64_t cycleLength=300000;uint64_t proposals=0;
 const auto start=std::chrono::steady_clock::now();
 for(uint64_t cycle=0;proposals<iterations;cycle++){
   // Every fourth cooling cycle starts independently at random. Other cycles
   // restart from this worker's own best, with fresh random perturbations.
   if(cycle%4==0||best.energy==INT32_MAX){for(int&i:current.s)i=(random.next()&1)?1:-1;current.recompute();}
   else {current=best;int flips=8+int(random.next()%57);for(int i=0;i<flips;i++){int p=random.index();current.flip(p,current.delta(p));}}
   const double high=cycle%4==0?3000.0:800.0;
   double temperature=high;
   for(uint64_t step=0;step<cycleLength&&proposals<iterations;step++,proposals++){
     if(step%512==0)temperature=high*std::pow(12.0/high,double(step)/cycleLength);
     int p=random.index();int first=current.delta(p);bool pair=(random.next()&7)==0;int q=-1,second=0;
     if(pair){current.flip(p,first);do{q=random.index();}while(q==p);second=current.delta(q);}
     const int change=first+second;
     bool accept=change<=0||random.unit()<std::exp(-double(change)/temperature);
     if(accept){if(pair)current.flip(q,second);else current.flip(p,first);}
     else if(pair)current.flip(p,-first);
     if(current.energy<best.energy){best=current;save(base,best,seed,proposals+1,cycle);}
   }
   // Integer recomputation detects any error in incremental flip accounting.
   State check=best;check.recompute();if(check.energy!=best.energy||check.c!=best.c){std::cerr<<"correlation consistency failure\n";return 1;}
   save(base,best,seed,proposals,cycle+1);
 }
 const double seconds=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
 std::cout<<"seed="<<seed<<" iterations="<<proposals<<" energy="<<best.energy<<" seconds="<<seconds<<"\n";
}
