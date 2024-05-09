source "/opt/conda/bin/activate" "/workspace/sv-callers/workflow/.snakemake/conda/4fd7fc84a9533a63c1f5c233dfb6f17f" &> /dev/null
#!/bin/bash
set -eu

outdir=$PREFIX/share/$PKG_NAME-$PKG_VERSION-$PKG_BUILDNUM
mkdir -p $outdir
mkdir -p $PREFIX/bin

cp -r * $outdir
rm -rf $outdir/share/demo
sed -i.bak 's/__file__/os.path.realpath(__file__)/' $outdir/bin/configManta.py
ln -s $outdir/bin/configManta.py $PREFIX/bin
