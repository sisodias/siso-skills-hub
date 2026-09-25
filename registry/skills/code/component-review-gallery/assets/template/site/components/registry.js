/* One import per component under review. A fresh gallery ships with a placeholder
   so it runs end to end; replace that import and ORDER with the client's own
   component once its assets are in place. */

import example from './example.js';

export const COMPONENTS = { [example.id]: example };

export const ORDER = [example.id];

export function getComponent(id) {
  return COMPONENTS[id] ?? null;
}
