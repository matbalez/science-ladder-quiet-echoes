// MIT License. Copyright (c) 2026 MatBalez and Science Ladder contributors.
// Two original data-artifact searches. No published candidate is used as a seed.
#include <array>
#include <cassert>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <limits>
#include <string>
#include <vector>
#include <algorithm>

constexpr int N=512;
using Seq=std::array<int,N>;
using Corr=std::array<int,N>;
struct Rng {
    uint64_t state;
    uint64_t next() {
        uint64_t z=(state+=0x9e3779b97f4a7c15ULL);
        z=(z^(z>>30))*0xbf58476d1ce4e5b9ULL;
        z=(z^(z>>27))*0x94d049bb133111ebULL;
        return z^(z>>31);
    }
};
Corr correlations(const Seq& s) {
    Corr c{};
    for(int k=1;k<N;k++) for(int i=0;i<N-k;i++) c[k]+=s[i]*s[i+k];
    return c;
}
int64_t energy(const Corr& c) {
    int64_t e=0; for(int k=1;k<N;k++) e+=int64_t(c[k])*c[k]; return e;
}
int64_t delta(const Seq& s,const Corr& c,int j) {
    int64_t de=0;const int factor=-2*s[j];
    for(int k=1;k<N;k++) {
        int d=factor*((j>=k?s[j-k]:0)+(j+k<N?s[j+k]:0));
        de+=int64_t(2*c[k]+d)*d;
    }
    return de;
}
void flip(Seq& s,Corr& c,int j) {
    const int factor=-2*s[j];
    for(int k=1;k<N;k++) c[k]+=factor*((j>=k?s[j-k]:0)+(j+k<N?s[j+k]:0));
    s[j]=-s[j];
}
void write(const Seq& s,const std::string& file) {
    std::ofstream out(file,std::ios::binary);if(!out)throw std::runtime_error("cannot write artifact");
    for(int sign:s)out<<(sign==1?'+':'-');out<<'\n';out.close();
}
void self_test() {
    Rng rng{9917};Seq s{};for(auto& x:s)x=(rng.next()&1)?1:-1;
    auto c=correlations(s);auto e=energy(c);
    for(int j=0;j<N;j++) {
        auto trial=s;trial[j]=-trial[j];assert(energy(correlations(trial))-e==delta(s,c,j));
    }
    for(int t=0;t<100;t++) {int j=rng.next()%N;auto d=delta(s,c,j);flip(s,c,j);e+=d;assert(c==correlations(s));assert(e==energy(c));}
}
bool prime(int p) {if(p<2)return false;for(int d=2;d*d<=p;d++)if(p%d==0)return false;return true;}

int main(int argc,char** argv) {
    if(argc<3){std::cerr<<"search random OUTPUT [restarts=64] [steps=1600] [seed=2026090401]\nsearch structured OUTPUT\nsearch self-test UNUSED\n";return 2;}
    std::string mode=argv[1],output=argv[2];self_test();
    if(mode=="self-test"){std::cout<<"incremental integer delta and correlation self-tests passed\n";return 0;}
    auto begin=std::chrono::steady_clock::now();Seq best{};int64_t best_e=std::numeric_limits<int64_t>::max();uint64_t examined=0,accepted=0;
    auto save=[&](const Seq& s,int64_t e,const std::string& origin){if(e>=best_e)return;assert(e==energy(correlations(s)));best=s;best_e=e;write(s,output);double seconds=std::chrono::duration<double>(std::chrono::steady_clock::now()-begin).count();std::cout<<"{\"event\":\"improvement\",\"energy\":"<<e<<",\"origin\":\""<<origin<<"\",\"evaluations\":"<<examined<<",\"elapsedSeconds\":"<<seconds<<"}"<<std::endl;};
    if(mode=="random") {
        int restarts=argc>3?std::stoi(argv[3]):64,steps=argc>4?std::stoi(argv[4]):1600;
        uint64_t seed=argc>5?std::stoull(argv[5]):2026090401ULL;Rng rng{seed};
        for(int restart=0;restart<restarts;restart++) {
            Seq s{};for(auto& x:s)x=(rng.next()&1)?1:-1;Corr c=correlations(s);int64_t e=energy(c);std::array<int,N> tabu{};save(s,e,"random-start-"+std::to_string(restart));
            for(int step=1;step<=steps;step++) {
                int chosen=-1,ties=0;int64_t chosen_delta=std::numeric_limits<int64_t>::max();
                for(int j=0;j<N;j++) {
                    int64_t d=delta(s,c,j);examined++;
                    if(tabu[j]>step&&e+d>=best_e)continue;
                    if(d<chosen_delta){chosen=j;chosen_delta=d;ties=1;}else if(d==chosen_delta&&rng.next()%uint64_t(++ties)==0)chosen=j;
                }
                if(chosen<0)throw std::runtime_error("all variables tabu");
                flip(s,c,chosen);e+=chosen_delta;accepted++;tabu[chosen]=step+34+int(rng.next()%52);
                save(s,e,"restart-"+std::to_string(restart)+"-step-"+std::to_string(step));
                if(step%128==0){assert(c==correlations(s));assert(e==energy(c));}
            }
        }
    } else if(mode=="structured") {
        // Exhaust all rotations of quadratic-residue sign sequences for each
        // prime449..1021. Repetition/truncation produces exactly512 signs.
        // This is a deterministic construction family, not stochastic descent.
        for(int p=449;p<=1021;p++) {
            if(!prime(p))continue;
            std::vector<int> residue(p,-1);residue[0]=1;
            for(int r=1;r<p;r++)residue[(r*r)%p]=1;
            for(int zero_sign:{1,-1}) {
                residue[0]=zero_sign;
                for(int rotation=0;rotation<p;rotation++) {
                    Seq s{};for(int i=0;i<N;i++)s[i]=residue[(i+rotation)%p];
                    auto e=energy(correlations(s));examined++;
                    save(s,e,"prime-"+std::to_string(p)+"-rotation-"+std::to_string(rotation)+"-zero-"+std::to_string(zero_sign));
                }
            }
        }
    } else {std::cerr<<"unknown strategy\n";return 2;}
    auto c=correlations(best);assert(best_e==energy(c));int peak=0;for(int k=1;k<N;k++)peak=std::max(peak,std::abs(c[k]));
    double seconds=std::chrono::duration<double>(std::chrono::steady_clock::now()-begin).count();
    std::cout<<"{\"event\":\"complete\",\"mode\":\""<<mode<<"\",\"energy\":"<<best_e<<",\"peakSidelobe\":"<<peak<<",\"evaluations\":"<<examined<<",\"acceptedMoves\":"<<accepted<<",\"elapsedSeconds\":"<<seconds<<",\"official\":false}"<<std::endl;
}
