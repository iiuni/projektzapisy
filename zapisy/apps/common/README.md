# What to put in this folder?

There is always a danger of clogging `common` and `utils` with too much stuff.
When there is too much stuff here, it becomes harder to find something useful
and make good use of it. The instructions set out here aim to prevent that from
happening.

## Rule I: Never create stuff in this folder

Files should only be moved here from other apps, once they turn out to be
equally useful in multiple apps. If you create a util (eg. a widget, a function)
for one app, it should live in this app's folder even if it is not logically
related to this app.

### Example

The `render-markdown` bundle had been created in `apps/offer/proposal` app and
had lived there until it found other uses. Only then it became a common asset.

## Rule II: Do not move stuff here if it is logically tied to some app

Some assets are used in multiple apps but their logic is strongly tied to one
app more than the others.

### Example

Course filters are used in three apps (`apps/enrollment/courses`,
`apps/enrollment/timetable`, `apps/offer/proposal`) but they are not
universal—there is no chance they will find other use than filtering courses.

##### Note

Some components in these filters may be universal and it may make sense moving them here **once** they find other use.
