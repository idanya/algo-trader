from pipeline.builders.loader import LoadersPipelines

if __name__ == '__main__':
    LoadersPipelines.build_daily_loader().run()

