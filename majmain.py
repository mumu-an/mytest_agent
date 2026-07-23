from api_method import rating_fastapi
import asyncio

async def main():
    await rating_fastapi.main()

if __name__ == '__main__':
    asyncio.run(main())
