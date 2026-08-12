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
    ]),
  });

export type KnowledgeSourceForm =
  z.infer<
    typeof knowledgeSourceSchema
  >;