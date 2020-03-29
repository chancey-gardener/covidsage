#!/usr/bin/python3

from fastapi import FastApi


app = FastApi()


@app.get("/")
async def root():
	return {"Message": "DOOOOOD"}


