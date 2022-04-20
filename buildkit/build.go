package main

import (
	"context"
	"os"

	"github.com/moby/buildkit/client/llb"
	// "github.com/moby/buildkit/util/system"
)

func main() {

	inputs := []llb.State{build(), coverage(), pylint()}
	out := llb.Merge(inputs)

	dt, err := out.Marshal(context.TODO(), llb.LinuxAmd64)
	if err != nil {
		panic(err)
	}
	llb.WriteTo(dt, os.Stdout)
}

func pythonFS() llb.State {
	return llb.Image("docker.io/library/alpine:latest").
		Run(llb.Shlex("apk add --no-cache python3 py3-pip py3-distutils-extra py3-wheel build-base gcc python3-dev zlib-dev jpeg-dev")).
		Root()
}

func appFS() (llb.State, llb.State) {
	py := pythonFS()

	working_dir := llb.Local("working-dir")

	r := copy(working_dir, "/requirements.txt", llb.Scratch(), "/requirements.txt")

	return py.Dir("/app").Run(llb.Shlex("pip install -r requirements.txt"), llb.AddMount("/app", r)).Root(), working_dir
}

func build() llb.State {
	app, working_dir := appFS()

	r := app.Run(llb.Shlex("python3 setup.py bdist"), llb.AddMount("/app", working_dir))
	ret := r.AddMount("/app/dist", llb.Scratch())

	return ret
}

func coverage() llb.State {
	app, working_dir := appFS()

	pip := app.Run(llb.Shlex("pip install coverage")).Root()

	r := pip.Dir("/app").AddEnv("COVERAGE_FILE", "/tmp/coverage").Run(llb.Shlex("coverage run -m unittest discover"), llb.AddMount("/app", working_dir, llb.Readonly)).
		Dir("/app").AddEnv("COVERAGE_FILE", "/tmp/coverage").Run(llb.Shlex("coverage html --directory /out/htmlcov"), llb.AddMount("/app", working_dir, llb.Readonly))

	ret := r.AddMount("/out", llb.Scratch())

	return ret
}

func pylint() llb.State {
	app, working_dir := appFS()

	pip := app.Run(llb.Shlex("pip install pylint")).Root()

	r := pip.Dir("/app").Run(llb.Shlex("pylint pngparser -f json --output /app/pylint/report.json"), llb.AddMount("/app", working_dir))

	ret := r.AddMount("/app/pylint", llb.Scratch())

	return ret
}

func copyAll(src llb.State, destPath string) llb.StateOption {
	return copyFrom(src, "/out", destPath)
}

// copyFrom has similar semantics as `COPY --from`
func copyFrom(src llb.State, srcPath, destPath string) llb.StateOption {
	return func(s llb.State) llb.State {
		return copy(src, srcPath, s, destPath)
	}
}

// copy copies files between 2 states using cp
func copy(src llb.State, srcPath string, dest llb.State, destPath string) llb.State {
	return dest.File(llb.Copy(src, srcPath, destPath, &llb.CopyInfo{
		AllowWildcard:  true,
		AttemptUnpack:  true,
		CreateDestPath: true,
	}))
}
