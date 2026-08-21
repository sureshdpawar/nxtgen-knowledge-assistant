import { z } from "zod";


export const knowledgeSourceSchema =
  z.object({
    name: z
      .string()
      .min(
        2,
        "Minimum 2 characters",
      )
      .max(100),

    type: z.enum([
      "UPLOAD",
      "WEBSITE",
    ]),

    baseUrl: z
      .string()
      .optional(),

    maxPages: z
      .number()
      .int()
      .min(1)
      .max(200),

    maxDepth: z
      .number()
      .int()
      .min(0)
      .max(10),
  })
  .superRefine(
    (
      values,
      context,
    ) => {
      if (
        values.type
        !== "WEBSITE"
      ) {
        return;
      }

      if (
        !values.baseUrl
        || values.baseUrl
          .trim()
          .length === 0
      ) {
        context.addIssue({
          code:
            z.ZodIssueCode.custom,
          path: [
            "baseUrl",
          ],
          message:
            "Website URL is required",
        });

        return;
      }

      try {
        const value =
          values.baseUrl
            .startsWith("http://")
          || values.baseUrl
            .startsWith("https://")
            ? values.baseUrl
            : `https://${values.baseUrl}`;

        new URL(value);
      } catch {
        context.addIssue({
          code:
            z.ZodIssueCode.custom,
          path: [
            "baseUrl",
          ],
          message:
            "Enter a valid website URL",
        });
      }
    },
  );


export type KnowledgeSourceForm =
  z.infer<
    typeof knowledgeSourceSchema
  >;