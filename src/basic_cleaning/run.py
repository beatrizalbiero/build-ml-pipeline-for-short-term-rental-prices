#!/usr/bin/env python
"""
Download from W&B the raw dataset and apply some basic data cleaning, exporting the result to a new artifact
"""
import argparse
import logging
import wandb
import pandas as pd


logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):

    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)

    run = wandb.init(project="nyc_airbnb", group="eda", save_code=True)
    local_path = wandb.use_artifact("sample.csv:latest").file()
    logger.info("Downloaded csv")
    df = pd.read_csv(local_path)

    # Remove outliers
    min_price = args.min_price
    max_price = args.max_price
    idx = df['price'].between(min_price, max_price)
    df = df[idx].copy()
    logger.info("Min price: {}, Max price: {}".format(df.price.min(), df.price.max()))
    logger.info("Removed Outliers")
    # Convert last_review to datetime
    df['last_review'] = pd.to_datetime(df['last_review'])
    logger.info("Converted last_review to datetime.")
    logger.info("{}".format(df.info()))
    # Set geo boundaries
    idx = df['longitude'].between(-74.25, -73.50) & df['latitude'].between(40.5, 41.2)
    df = df[idx].copy()

    #Upload to W&B
    df.to_csv("clean_sample.csv", index=False)
    artifact = wandb.Artifact(
         args.output_artifact,
         type=args.output_type,
         description=args.output_description
        )
    artifact.add_file("clean_sample.csv")
    run.log_artifact(artifact)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="basic cleaning")


    parser.add_argument(
        "--input_artifact",
        type=str,
        help="Dataset downloaded from W&B",
        required=True
    )

    parser.add_argument(
        "--output_artifact",
        type=str,
        help="Dataframe cleaned",
        required=True
    )

    parser.add_argument(
        "--output_type",
        type=str,
        help="str (CSV)",
        required=True
    )

    parser.add_argument(
        "--output_description",
        type=str,
        help="Cleaned dataframe, removed outliers and changed last_review column",
        required=True
    )

    parser.add_argument(
        "--min_price",
        type=float,
        help="The minimum accepted price",
        required=True
    )

    parser.add_argument(
        "--max_price",
        type=float,
        help="The maximum accepted price",
        required=True
    )


    args = parser.parse_args()

    go(args)
