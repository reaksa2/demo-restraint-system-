import { useEffect, useState, useMemo } from "react";
import { menuApi } from "../services/resources";
import { useAuth } from "../stores/authStore";
import { LogOut } from "lucide-react";

import { resolveMediaUrl } from "../services/api";

export default function StaffMenuPage() {
  const { logout } = useAuth();
  const [menu, setMenu] = useState(null);
  const [activeCategory, setActiveCategory] = useState("all");
  const [error, setError] = useState("");

  useEffect(() => {
    menuApi
      .get()
      .then(setMenu)
      .catch(() =>
        setError(
          "Could not load the menu. Ask a manager to check your zone assignment.",
        ),
      );
  }, []);

  const foodsByCategory = useMemo(() => {
    if (!menu) return [];
    if (activeCategory === "all") return menu.foods;
    return menu.foods.filter((f) => f.category_id === activeCategory);
  }, [menu, activeCategory]);

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-paper px-6 text-center">
        <div>
          <p className="text-clay">{error}</p>
          <button
            onClick={logout}
            className="mt-3 text-sm text-slate underline"
          >
            Sign out
          </button>
        </div>
      </div>
    );
  }

  if (!menu) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-paper text-slate">
        Loading menu…
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-paper">
      <header className="border-b border-sand bg-white">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-5">
          <div className="flex items-center gap-3">
            {menu.brand.logo_url && (
              <img
                src={resolveMediaUrl(menu.brand.logo_url)}
                alt=""
                className="h-11 w-11 rounded-md object-cover"
              />
            )}
            <div>
              <h1 className="font-khmer-display text-2xl text-ink">
                {menu.brand.name_kh}
              </h1>
              <p className="text-sm text-slate">{menu.brand.name_en}</p>
            </div>
          </div>
          <button
            onClick={logout}
            className="flex items-center gap-1.5 text-xs text-slate hover:text-ink"
          >
            <LogOut size={13} /> Sign out
          </button>
        </div>

        {menu.categories.length > 0 && (
          <div className="mx-auto flex max-w-5xl gap-1 overflow-x-auto px-6 pb-3">
            <CategoryTab
              active={activeCategory === "all"}
              onClick={() => setActiveCategory("all")}
              labelEn="All"
              labelKh="ទាំងអស់"
            />
            {menu.categories.map((c) => (
              <CategoryTab
                key={c.id}
                active={activeCategory === c.id}
                onClick={() => setActiveCategory(c.id)}
                labelEn={c.name_en}
                labelKh={c.name_kh}
              />
            ))}
          </div>
        )}
      </header>

      <main className="mx-auto max-w-5xl px-6 py-8">
        {foodsByCategory.length === 0 ? (
          <p className="py-16 text-center text-slate">
            No foods in this category yet.
          </p>
        ) : (
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {foodsByCategory.map((food) => (
              <FoodCard key={food.id} food={food} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

function CategoryTab({ active, onClick, labelEn, labelKh }) {
  return (
    <button
      onClick={onClick}
      className={`flex-shrink-0 rounded-full px-4 py-1.5 text-sm transition-colors ${
        active ? "bg-ink text-white" : "bg-sand/60 text-slate hover:bg-sand"
      }`}
    >
      <span className="font-khmer">{labelKh}</span>{" "}
      <span className="opacity-70">{labelEn}</span>
    </button>
  );
}

function FoodCard({ food }) {
  return (
    <div
      className={`overflow-hidden rounded-lg border border-sand bg-white ${!food.is_available ? "opacity-60" : ""}`}
    >
      <div className="aspect-[4/3] bg-sand">
        {food.image_url && (
          <img
            src={resolveMediaUrl(food.image_url)}
            alt={food.name_en}
            className="h-full w-full object-cover"
          />
        )}
      </div>
      <div className="p-4">
        <p className="font-khmer-display text-lg leading-tight text-ink">
          {food.name_kh}
        </p>
        <p className="font-display text-sm text-slate">{food.name_en}</p>

        {(food.description_kh || food.description_en) && (
          <div className="mt-2 space-y-0.5">
            {food.description_kh && (
              <p className="font-khmer text-xs text-slate">
                {food.description_kh}
              </p>
            )}
            {food.description_en && (
              <p className="text-xs text-slate">{food.description_en}</p>
            )}
          </div>
        )}

        <div className="mt-3 flex items-center justify-between">
          {!food.is_available ? (
            <span className="text-sm font-medium text-clay">Unavailable</span>
          ) : food.price ? (
            <span className="font-display text-xl text-marigold-dark">
              ${Number(food.price.price).toFixed(2)}
              {food.price.is_discounted && (
                <span className="ml-1.5 text-xs font-sans text-moss">
                  Discount
                </span>
              )}
            </span>
          ) : (
            <span className="text-sm text-slate">Price not set</span>
          )}
        </div>
      </div>
    </div>
  );
}
