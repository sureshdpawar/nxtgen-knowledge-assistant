import {
  z,
} from "zod";


export const knowledgeSourceSchema =
  z.object({

    name: z
      .string()
      .min(
        2,
        "Minimum 2 characters",
      )
      .max(
        100,
      ),

    type: z.enum([
      "UPLOAD",
      "WEBSITE",
      "GOOGLE_DRIVE",
    ]),

    baseUrl: z
      .string()
      .optional(),

    maxPages: z
      .number()
      .int()
      .min(
        1,
      )
      .max(
        200,
      ),

    maxDepth: z
      .number()
      .int()
      .min(
        0,
      )
      .max(
        10,
      ),

    driveFolderUrl: z
      .string()
      .optional(),

    driveRecursive: z
      .boolean(),

  })
  .superRefine(
    (
      values,
      context,
    ) => {

      /*
       * Website
       */
      if (
        values.type
        === "WEBSITE"
      ) {

        if (
          !values.baseUrl
          || values.baseUrl
            .trim()
            .length === 0
        ) {
          context.addIssue({
            code:
              z.ZodIssueCode
                .custom,

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
              .startsWith(
                "http://",
              )
            || values.baseUrl
              .startsWith(
                "https://",
              )
              ? values.baseUrl
              : (
                `https://${values.baseUrl}`
              );

          new URL(
            value,
          );

        } catch {
          context.addIssue({
            code:
              z.ZodIssueCode
                .custom,

            path: [
              "baseUrl",
            ],

            message:
              "Enter a valid website URL",
          });
        }
      }


      /*
       * Google Drive
       */
      if (
        values.type
        === "GOOGLE_DRIVE"
      ) {

        const driveFolderUrl =
          values
            .driveFolderUrl
            ?.trim();

        if (
          !driveFolderUrl
        ) {
          context.addIssue({
            code:
              z.ZodIssueCode
                .custom,

            path: [
              "driveFolderUrl",
            ],

            message:
              "Google Drive folder URL is required",
          });

          return;
        }

        const isFolderUrl =
          driveFolderUrl.includes(
            "drive.google.com",
          )
          && driveFolderUrl.includes(
            "/folders/",
          );

        const looksLikeRawId =
          !driveFolderUrl.includes(
            "/",
          )
          && driveFolderUrl.length
            >= 10;

        if (
          !isFolderUrl
          && !looksLikeRawId
        ) {
          context.addIssue({
            code:
              z.ZodIssueCode
                .custom,

            path: [
              "driveFolderUrl",
            ],

            message:
              "Enter a Google Drive folder URL or folder ID",
          });
        }
      }

    },
  );


export type KnowledgeSourceForm =
  z.infer<
    typeof knowledgeSourceSchema
  >;