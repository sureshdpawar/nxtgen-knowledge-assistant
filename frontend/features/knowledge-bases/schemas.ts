import { z } from "zod";

export const knowledgeBaseSchema =
  z.object({
    name: z
      .string()
      .min(
        3,
        "Minimum 3 characters",
      )
      .max(100),

    description: z
      .string()
      .max(500)
      .optional(),

    visibility: z.enum([
      "PRIVATE",
      "PUBLIC",
    ]),
  });

export type KnowledgeBaseForm =
  z.infer<
    typeof knowledgeBaseSchema
  >;