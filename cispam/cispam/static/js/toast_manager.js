/**
 * @global
 * @interface Window
 * @property {ToastManager} toastManager - The singleton instance of ToastManager.
 */

/**
 * Configuration object defining the visual styles and content for different toast notification types.
 * Supports localization via the global `gettext` function if available.
 * @type {Object.<string, {bg: string, border: string, iconBg: string, iconColor: string, titleColor: string, textColor: string, progressColor: string, title: string, icon: string}>}
 */
const toastStyles = {
  success: {
    bg: "bg-white",
    border: "border-emerald-500",
    iconBg: "bg-emerald-500",
    iconColor: "text-emerald-600",
    titleColor: "text-emerald-800",
    textColor: "text-slate-600",
    progressColor: "bg-emerald-500",
    title: typeof gettext === "function" ? gettext("Succès") : "Succès",
    icon: `<svg xmlns="http://www.w3.org/2000/svg" class="size-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>`,
  },
  warning: {
    bg: "bg-white",
    border: "border-amber-500",
    iconBg: "bg-amber-500",
    iconColor: "text-amber-600",
    titleColor: "text-amber-800",
    textColor: "text-slate-600",
    progressColor: "bg-amber-500",
    title: typeof gettext === "function" ? gettext("Attention") : "Attention",
    icon: `<svg class="size-2.5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/>
                    <path d="M12 9v4"/>
                    <path d="M12 17h.01"/>
                </svg>`,
  },
  info: {
    bg: "bg-white",
    border: "border-sky-500",
    iconBg: "bg-sky-500",
    iconColor: "text-sky-600",
    titleColor: "text-sky-800",
    textColor: "text-slate-600",
    progressColor: "bg-sky-500",
    title: typeof gettext === "function" ? gettext("Information") : "Information",
    icon: `<span class="text-xs font-bold">i</span>`,
  },
  error: {
    bg: "bg-white",
    border: "border-rose-500",
    iconBg: "bg-rose-500",
    iconColor: "text-rose-600",
    titleColor: "text-rose-800",
    textColor: "text-slate-600",
    progressColor: "bg-rose-500",
    title: typeof gettext === "function" ? gettext("Erreur") : "Erreur",
    icon: `<svg xmlns="http://www.w3.org/2000/svg" class="size-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M18 6 6 18"/>
                    <path d="m6 6 12 12"/>
                </svg>`,
  },
};

/**
 * Manages the lifecycle, positioning, and rendering of toast notifications.
 * Handles responsive animations and automatic dismissal.
 */
class ToastManager {
  /**
   * Initializes the toast container and injects required CSS animations into the document head.
   * @constructor
   */
  constructor() {
    /** * Object holding the four corner containers.
     * @type {Object.<string, HTMLDivElement>}
     */
    this.containers = {};

    // Define the 4 standard corners
    const positions = ["top-left", "top-right", "bottom-left", "bottom-right"];

    positions.forEach((pos) => {
      const container = document.createElement("div");
      container.id = `toast-container-${pos}`;

      // Base classes: fixed, z-index, flex column
      // We use a helper method to set the specific corner CSS
      container.className =
        "fixed z-[9999999] flex flex-col gap-2 w-full max-w-[85vw] ms:max-w-xs md:max-w-sm pointer-events-none transition-all duration-400";

      this.containers[pos] = container;
      this.applyContainerStyles(container, pos);
      document.body.appendChild(container);
    });

    this.injectStyles();
  }

  create() {
    return new ToastBuilder(this);
  }

  /**
   * Applies specific CSS positioning to a container based on its corner.
   * @param {HTMLDivElement} container
   * @param {string} pos
   * @private
   */
  applyContainerStyles(container, pos) {
    const isMobile = window.innerWidth < 768;

    if (isMobile) {
      container.style.left = "50%";
      container.style.transform = "translateX(-50%)";
      if (pos.includes("top")) container.style.top = "1rem";
      else container.style.bottom = "1rem";

      // Hide containers that aren't the primary mobile ones to avoid overlap
      // Usually mobile only uses one "active" side (top or bottom)
    } else {
      const [y, x] = pos.split("-");
      container.style[y] = "1rem";
      container.style[x] = "1rem";
    }
  }

  /**
   *  Injects the CSS keyframes and utility classes for toast animations (slide-in/out and progress bar).
   * @private
   */
  injectStyles() {
    const styles = `
            [id^="toast-container-"] > div { pointer-events: auto; }
            @keyframes slide-in-right { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
            @keyframes slide-out-right { from { transform: translateX(0); opacity: 1; } to { transform: translateX(100%); opacity: 0; } }
            @keyframes slide-in-left { from { transform: translateX(-100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
            @keyframes slide-out-left { from { transform: translateX(0); opacity: 1; } to { transform: translateX(-100%); opacity: 0; } }
            @keyframes slide-in-bottom { from { transform: translateY(100%); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
            @keyframes slide-out-bottom { from { transform: translateY(0); opacity: 1; } to { transform: translateY(100%); opacity: 0; } }
            @keyframes slide-in-top { from { transform: translateY(-100%); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
            @keyframes slide-out-top { from { transform: translateY(0); opacity: 1; } to { transform: translateY(-100%); opacity: 0; } }

            .animate-slide-in-right { animation: slide-in-right 0.3s ease-out forwards; }
            .animate-slide-out-right { animation: slide-out-right 0.3s ease-in forwards; }
            .animate-slide-in-left { animation: slide-in-left 0.3s ease-out forwards; }
            .animate-slide-out-left { animation: slide-out-left 0.3s ease-in forwards; }
            .animate-slide-in-bottom { animation: slide-in-bottom 0.3s ease-out forwards; }
            .animate-slide-out-bottom { animation: slide-out-bottom 0.3s ease-in forwards; }
            .animate-slide-in-top { animation: slide-in-top 0.3s ease-out forwards; }
            .animate-slide-out-top { animation: slide-out-top 0.3s ease-in forwards; }

            @keyframes progress { from { width: 100%; } to { width: 0%; } }
            .progress-bar-toast { animation: progress linear forwards; }
        `;
    const styleSheet = document.createElement("style");
    styleSheet.textContent = styles;
    document.head.appendChild(styleSheet);
  }

  /**
   * Creates and displays a new toast notification.
   * @param {string} message - The main content of the toast.
   * @param {'success'|'warning'|'info'|'error'} [type="info"] - The notification style type.
   * @param {'top-left'|'top-right'|'bottom-left'|'bottom-right'} [position="top-right"] - Screen corner position.
   * @param {number} [duration=4000] - Visibility time in milliseconds before automatic dismissal.
   * @param {string|null} icon - Optional custom icon HTML. If not provided, it will use the default icon based on the type.
   * @param {string|null} title - The title of the toast, if not provided it will use the default title based on the type.
   */
  showToast(
    message,
    type = "info",
    position = "top-right",
    duration = 4000,
    icon = null,
    title = null,
  ) {
    const style = toastStyles[type] || toastStyles.info;
    const targetContainer =
      this.containers[position] || this.containers["top-right"];

    const existingToastsCount = targetContainer.children.length;
    const staggerDelay = existingToastsCount * 100;

    const isMobile = window.innerWidth < 768;
    let slideIn, slideOut;

    if (isMobile) {
      slideIn = position.includes("top")
        ? "animate-slide-in-top"
        : "animate-slide-in-bottom";
      slideOut = position.includes("top")
        ? "animate-slide-out-top"
        : "animate-slide-out-bottom";
    } else {
      slideIn = position.includes("left")
        ? "animate-slide-in-left"
        : "animate-slide-in-right";
      slideOut = position.includes("left")
        ? "animate-slide-out-left"
        : "animate-slide-out-right";
    }

    const toast = document.createElement("div");
    toast.className = `w-full bg-white border border-gray-300 p-3 md:p-4 rounded-lg shadow-md ${slideIn} relative overflow-hidden transform transition-all`;

    toast.style.animationDelay = `${staggerDelay}ms`;
    // On cache le toast initialement pour éviter qu'il clignote avant l'animation
    toast.style.opacity = "0";
    toast.style.animationFillMode = "forwards";

    // Use a data attribute to store the out-animation for closeAllToasts logic
    toast.dataset.animateOut = slideOut;
    toast.dataset.animateIn = slideIn;

    toast.innerHTML = `
            <div class="">
                <div>
                    <div class="flex items-start md:items-center gap-3 w-full">
                        ${
                          icon ??
                          `<div class="${style.iconBg} text-white rounded-full size-4 flex items-center justify-center shrink-0">
                                ${style.icon}
                            </div> `
                        }

                        <h2 class="font-montserrat text-xs md:text-sm lg:text-base font-bold leading-tight">${title ?? style.title}</h2>
                    </div>
                    <p class="font-montserrat text-neutral-600 text-xs md:text-sm leading-relaxed mt-4">${message}</p>
                </div>
                <button class="text-white bg-neutral-400 cursor-pointer hover:bg-neutral-700 flex justify-center items-center rounded-full close-toast shrink-0 absolute right-2 top-2"
                style="animation-duration: ${duration}ms; animation-delay: ${staggerDelay}ms">
                    <svg xmlns="http://www.w3.org/2000/svg" class="size-3 m-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
            </div>
            <div class="absolute bottom-0 left-0 h-1 ${style.progressColor} progress-bar-toast" style="animation-duration: ${duration}ms"></div>
        `;

    targetContainer.appendChild(toast);

    const removeToast = () => {
      if (!toast.classList.contains(slideOut)) {
        toast.style.animationDelay = "0ms";
        toast.classList.remove(slideIn);
        toast.classList.add(slideOut);
        toast.addEventListener("animationend", () => toast.remove(), {
          once: true,
        });
        setTimeout(() => toast.remove(), 400);
      }
    };

    toast.querySelector(".close-toast").onclick = removeToast;
    setTimeout(removeToast, duration + staggerDelay);
  }

  /**
   * Closes all toasts across all 4 containers.
   */
  closeAllToasts() {
    Object.values(this.containers).forEach((container) => {
      container.querySelectorAll("div[data-animate-out]").forEach((toast) => {
        const out = toast.dataset.animateOut;
        const inAnim = toast.dataset.animateIn;
        toast.classList.remove(inAnim);
        toast.classList.add(out);
        setTimeout(() => toast.remove(), 400);
      });
    });
  }
}

/**
 * Builder class for configuring and displaying toasts fluently.
 * @class
 */
class ToastBuilder {
  /**
   * @param {ToastManager} manager - The ToastManager instance.
   */
  constructor(manager) {
    this.manager = manager;
    this.config = {
      message: "",
      type: "info",
      position: "top-right",
      duration: 4000,
      icon: null,
      title: null,
    };
  }

  /**
   * Sets the toast message.
   * @param {string} message
   * @returns {ToastBuilder}
   */
  setMessage(message) {
    this.config.message = message;
    return this;
  }

  /**
   * Sets the toast type ('success', 'warning', 'info', 'error').
   * @param {'success'|'warning'|'info'|'error'} type
   * @returns {ToastBuilder}
   */
  setType(type) {
    this.config.type = type;
    return this;
  }

  /**
   * Sets the screen corner position.
   * @param {'top-left'|'top-right'|'bottom-left'|'bottom-right'} position
   * @returns {ToastBuilder}
   */
  setPosition(position) {
    this.config.position = position;
    return this;
  }

  /**
   * Sets the display duration in ms.
   * @param {number} duration
   * @returns {ToastBuilder}
   */
  setDuration(duration) {
    this.config.duration = duration;
    return this;
  }

  /**
   * Sets a custom title for the toast.
   * @param {string} title
   * @returns {ToastBuilder}
   */
  setTitle(title) {
    this.config.title = title;
    return this;
  }

  /**
   * Sets a custom HTML icon.
   * @param {string} icon
   * @returns {ToastBuilder}
   */
  setIcon(icon) {
    this.config.icon = icon;
    return this;
  }

  /**
   * Triggers the toast display via the manager.
   */
  show() {
    const { message, type, position, duration, icon, title } = this.config;
    this.manager.showToast(message, type, position, duration, icon, title);
  }
}

/** @type {ToastManager} */
const toastManager = new ToastManager();
/** @type {ToastManager} */
window.toastManager = toastManager;
