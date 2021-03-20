
export function get_css_var(name) {
  return getComputedStyle(document.documentElement)
    .getPropertyValue(name);
}
