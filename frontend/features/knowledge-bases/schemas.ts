import {
  z,
} from "zod";


export const PLATFORM_DEFAULT_CHUNK_SIZE =
  1000;

export const PLATFORM_DEFAULT_CHUNK_OVERLAP =
  200;

export const PLATFORM_DEFAULT_TOP_K =
  5;


const optionalInteger = (
  min: number,
  max: number,
  label: string,
) =>
  z.preprocess(
    (
      value,
    ) => {
      if (
        value === ""
        || value === undefined
        || value === null
      ) {
        return null;
      }

      const parsed =
        Number(
          value,
        );

      return parsed;
    },
    z
      .number({
        message:
          `${label} must be a number`,
      })
      .int(
        `${label} must be an integer`,
      )
      .min(
        min,
        `${label} must be at least ${min}`,
      )
      .max(
        max,
        `${label} must be at most ${max}`,
      )
      .nullable(),
  );


export const knowledgeBaseSchema =
  z
    .object({
      name:
        z
          .string()
          .min(
            3,
            "Minimum 3 characters",
          )
          .max(
            100,
          ),

      description:
        z
          .string()
          .max(
            500,
          )
          .optional(),

      visibility:
        z.enum([
          "PRIVATE",
          "PUBLIC",
        ]),

      chunk_size:
        optionalInteger(
          100,
          4000,
          "Chunk size",
        ),

      chunk_overlap:
        optionalInteger(
          0,
          1000,
          "Chunk overlap",
        ),

      top_k:
        optionalInteger(
          1,
          20,
          "Top K",
        ),
    })
    .superRefine(
      (
        values,
        context,
      ) => {
        const chunkSize =
          values.chunk_size
          ?? PLATFORM_DEFAULT_CHUNK_SIZE;

        const chunkOverlap =
          values.chunk_overlap
          ?? PLATFORM_DEFAULT_CHUNK_OVERLAP;

        if (
          chunkOverlap
          >= chunkSize
        ) {
          context.addIssue({
            code:
              z.ZodIssueCode.custom,

            path: [
              "chunk_overlap",
            ],

            message:
              "Chunk overlap must be less than chunk size",
          });
        }
      },
    );


/*
 * Raw values received by
 * React Hook Form before
 * Zod preprocessing.
 */
export type KnowledgeBaseFormInput =
  z.input<
    typeof knowledgeBaseSchema
  >;


/*
 * Validated / transformed values
 * produced by Zod.
 *
 * chunk_size,
 * chunk_overlap,
 * top_k
 *
 * become:
 *
 * number | null
 */
export type KnowledgeBaseForm =
  z.output<
    typeof knowledgeBaseSchema
  >;