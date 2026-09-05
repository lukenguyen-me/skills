# Past Build Export Schema Reference

Complete TypeScript type definitions for the Past Build import format.

## ExportedProject (Full Schema)

```typescript
interface ExportedProject {
  /** Export format version - must be 1 */
  version: number;
  /** Project name */
  name: string;
  /** Project description */
  description: string;
  /** Project status: ongoing | finished */
  projectStatus?: 'ongoing' | 'finished';
  /** Project date (YYYY-MM-DD) */
  projectDate?: string;
  /** Project sections with media */
  sections: ExportedSection[];
  /** External project links */
  links?: ProjectLink[];
  /** Export timestamp (ISO) */
  exportedAt: string;
}
```

## ExportedSection

```typescript
interface ExportedSection {
  /** Section ID (UUID v4) */
  id: string;
  /** Section title */
  title: string;
  /** Optional subtitle */
  subtitle?: string;
  /** Display order (0, 1, 2, ...) */
  order: number;
  /** Media files (empty for JSON-only import) */
  media: ExportedMedia[];
}
```

## ExportedMedia

```typescript
interface ExportedMedia {
  /** Media ID (UUID v4) */
  id: string;
  /** Original filename */
  filename: string;
  /** Export filename in ZIP */
  exportFilename: string;
  /** MIME type (image/jpeg, video/mp4, etc.) */
  type: string;
  /** File size in bytes */
  size: number;
  /** Display order */
  order: number;
}
```

## ProjectLink

```typescript
interface ProjectLink {
  /** Link ID (UUID v4) */
  id: string;
  /** Link text (e.g., "GitHub", "Live Demo") */
  text: string;
  /** URL */
  url: string;
}
```

## File Limits

| Media Type | Max Size | Allowed Types |
|------------|----------|---------------|
| Images | 5MB | jpeg, png, gif, webp |
| Videos | 50MB | mp4, webm, quicktime |

**Note:** JSON-only import does not support media files. Use ZIP export for projects with screenshots/videos.
