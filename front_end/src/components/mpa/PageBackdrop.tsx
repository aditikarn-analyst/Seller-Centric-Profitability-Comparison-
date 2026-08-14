import { BarChart3, IndianRupee, Package, ShoppingBag, TrendingUp } from "lucide-react";

/** Purely decorative page background: mesh blobs, dotted grid, floating icons. */
export function PageBackdrop() {
  return (
    <div aria-hidden className="pointer-events-none absolute inset-0 -z-10 overflow-hidden">
      <div className="absolute -left-32 -top-40 size-[34rem] rounded-full bg-primary/20 blur-[120px]" />
      <div className="absolute -right-40 top-10 size-[30rem] rounded-full bg-secondary/15 blur-[130px]" />
      <div className="absolute left-1/3 top-[38rem] size-[28rem] rounded-full bg-accent/12 blur-[130px]" />

      <div className="dot-grid absolute inset-0 opacity-[0.06]" />

      <div className="absolute left-[6%] top-24 size-24 rounded-full border border-primary/15" />
      <div className="absolute right-[12%] top-[22rem] size-40 rounded-full border border-secondary/12" />
      <div className="absolute left-[42%] top-[10rem] size-16 rounded-full border border-accent/15" />

      <ShoppingBag className="float-soft absolute left-[8%] top-[9rem] size-10 text-primary/15" />
      <BarChart3
        className="float-soft absolute right-[9%] top-[7rem] size-12 text-secondary/15"
        style={{ animationDelay: "1.4s" }}
      />
      <IndianRupee
        className="float-soft absolute left-[46%] top-[3.5rem] size-9 text-accent/20"
        style={{ animationDelay: "2.6s" }}
      />
      <Package
        className="float-soft absolute right-[22%] top-[20rem] size-10 text-primary/12"
        style={{ animationDelay: "0.8s" }}
      />
      <TrendingUp
        className="float-soft absolute left-[14%] top-[26rem] size-11 text-positive/15"
        style={{ animationDelay: "3.2s" }}
      />
    </div>
  );
}
